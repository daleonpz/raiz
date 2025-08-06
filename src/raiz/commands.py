# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

# TODO: should i update the yaml always after each command, bzw after each update of the database?
#       use sync_to_yaml always after each command?
#       1. rename variables as _XXX to indicate they are private
from raiz.utils.database import RequirementsDB
from raiz.utils.report_generator import ReportWriter

import typer
import os
from pathlib import Path
from robot.api import ExecutionResult
from typing import Optional
import yaml
from collections import defaultdict
from datetime import datetime
import logging
import json
from rich.traceback import install
install(show_locals=True)

db = RequirementsDB()

REQS_DIR = Path("requirements")
REQS_DIR.mkdir(exist_ok=True)
REQ_FILE = REQS_DIR / "requirements.yaml"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def add():
    """Add a new requirement interactively."""
    description = typer.prompt("Description")
    req_type = typer.prompt("Type [functional, non-functional, constraint]")
    domain = typer.prompt("Domain [e.g., logging, ble, data-processing]")

    db.add_requirement(description=description, req_type=req_type, domain=domain)

def remove(
    req_id: int = typer.Argument(..., help="Requirement ID to remove (e.g., 1)")
):
    """Remove a requirement by ID and renumber the rest."""
    if req_id < 1:
        typer.echo("Requirement ID must be greater than 0.")
        raise typer.Exit(code=1)

    db.rm(req_id)

def update(
    req_id: int = typer.Argument(..., help="Requirement ID to update (e.g., 1)"),
    field: Optional[str] = typer.Option(None, '--field', '-f', help="Field to update (description, type, domain)"),
    value: Optional[str] = typer.Option(None, '--value', '-v', help="New value for the field")
):
    """Update a requirement by REQ ID. Interactive or field-based."""
    db.update_requirement(req_id, field, value)

def show_requirements(
    req_type: Optional[str] = typer.Option(None,'--type', help="Filter by requirement type (functional, non-functional, constraint)"), 
    domain: Optional[str] = typer.Option(None, help="Filter by requirement domain (e.g., logging, ble, data-processing)"),
    json: Optional[bool] = typer.Option(False, help="Output in JSON format")
):
    """Show requirements with optional filtering by type/domain."""
    db.show_requirements(req_type, domain, json)

def show_types():
    """Show all unique types."""
    db.show_characteristic("type")

def show_domains():
    """Show all unique domains."""
    db.show_characteristic("domain")

def sync_to_yaml( 
        file: Optional[Path] = typer.Option(REQ_FILE, help="Path to output YAML file")
):
    """Dump current SQLite requirements to YAML."""
    reqs = db.get_requirements()

    if file:
        REQ_FILE = Path(file)
        typer.echo(f"Using provided YAML file: {REQ_FILE}")

    if isinstance(reqs, defaultdict):
        reqs = dict(reqs)

    # flat list for YAML it's consistent with the original format
    flat_list = []
    for req_id, req_data in reqs.items():
        entry = {"id": req_id}
        entry.update(req_data)
        flat_list.append(entry)

    with open(REQ_FILE, "w") as f:
        yaml.dump(flat_list, f, default_flow_style=False, sort_keys=False)

    typer.echo(f"Exported {len(reqs)} requirements to {REQ_FILE}")

def sync_from_yaml(
    file: Optional[Path] = typer.Option(REQ_FILE, help="Path to YAML file with requirements")
):
    """Import requirements from YAML into SQLite (overwrites DB)."""
    if file:
        REQ_FILE = Path(file)
        typer.echo(f"Using provided YAML file: {REQ_FILE}")

    if not REQ_FILE.exists():
        typer.echo(f"Error: {REQ_FILE} not found.")
        raise typer.Exit()

    with open(REQ_FILE, "r") as f:
        reqs = yaml.safe_load(f)

    db.create_from_yaml(reqs)
    typer.echo(f"Requirements imported from {REQ_FILE}")


def _default_stat():
    return {
        "total_requirements": 0,
        "tested_requirements": 0,
        "total_tests": 0,
        "passed_tests": 0,
        "pass_rate": 0.0,
        "coverage_rate": 0.0
    }

def _finalize(stat):
    if stat["total_requirements"]:
        stat["coverage_rate"] = round(stat["tested_requirements"] / stat["total_requirements"] * 100, 2)
        if stat["total_tests"]:
            stat["pass_rate"] = round(stat["passed_tests"] / stat["total_tests"] * 100, 2)
            # Remove raw passed_tests and total_tests if not needed
            del stat["passed_tests"]
            del stat["total_tests"]
def trace(
    output: str = typer.Option("traceability", help="Output report filename"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    fmt: str = typer.Option("json", help="Output format: console, json"),
    domain: Optional[str] = typer.Option(None, help="Filter by domain (only in console)"),
    req_type: Optional[str] = typer.Option(None,'--type', help="Filter by requirement type (only in console)"),
    detail: bool = typer.Option(False, help="Show detailed trace report (only in console)")
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    if not Path(robot_output).exists():
        typer.echo(f"Robot output file '{robot_output}' not found.")
        raise typer.Exit()

    result = ExecutionResult(robot_output)

    req_map = defaultdict(list)

    root_source = result.suite.source

    for suite in result.suite.suites:
        suite_filename = os.path.basename(suite.source or root_source)
        for test in suite.tests:
            for tag in test.tags:
                if tag.startswith("REQ-"):
                    logging.debug(f"Found REQ tag: {tag} in test {test.name} in suite {suite_filename}")
                    req_map.setdefault(tag, []).append((suite_filename, test.name, test.status))

    logging.debug(f"REQ Map: {json.dumps(req_map, indent=2)}")

    reqs = db.get_requirements()
    logging.debug(f"Requirements List (REQs): {json.dumps(reqs, indent=2)}")

    for req_id in reqs:
        reqs[req_id]["linked_tests"] = [test[1] for test in req_map.get(req_id, [])]
        reqs[req_id]["test_results"] = req_map.get(req_id, [])

    logging.debug(f"Updated Requirements with Test Results: {json.dumps(reqs, indent=2)}")

    stats = _default_stat()
    detailed_stats = {
            "domains": defaultdict(_default_stat),
            "types": defaultdict(_default_stat)
    }

    # Process reqs
    for req in reqs.values():
        rdomain = req["domain"]
        rtype = req["type"]
        tested = bool(req["linked_tests"])
        total_tests = len(req["test_results"])
        passed_count = sum(1 for test in req["test_results"] if test[2] == "PASS")

        # Update global stats
        stats["total_requirements"] += 1
        if tested:
            stats["tested_requirements"] += 1
        stats["total_tests"] += total_tests
        stats["passed_tests"] += passed_count

        # Update domain stats
        d = detailed_stats["domains"][rdomain]
        d["total_requirements"] += 1
        if tested:
            d["tested_requirements"] += 1
        d["total_tests"] += total_tests
        d["passed_tests"] += passed_count

        # Update type stats
        t = detailed_stats["types"][rtype]
        t["total_requirements"] += 1
        if tested:
            t["tested_requirements"] += 1
        t["total_tests"] += total_tests
        t["passed_tests"] += passed_count

    _finalize(stats)
    for group in ["domains", "types"]:
        for key, val in detailed_stats[group].items():
            _finalize(val)

    # Output
    logging.debug(f"Final Stats: {json.dumps(stats, indent=2)}")
    logging.debug(f"Detailed Stats: {json.dumps(detailed_stats, indent=2)}")

    report = {
        "timestamp": datetime.now().isoformat(),
        "coverage": stats,
        "report": reqs,
        "detailed_report": {
            "domains": dict(detailed_stats["domains"]),
            "types": dict(detailed_stats["types"])
        }
    }
    writer = ReportWriter(report)

    for req_id, req_data in reqs.items():
        tests = req_data["linked_tests"]
        uuid = req_data.get("uuid")
        db.link_tests(tests=tests, uuid=uuid)

    writer.write(fmt, output, domain, req_type, detail)
