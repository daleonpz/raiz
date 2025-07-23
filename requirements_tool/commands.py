# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
from requirements_tool.utils.database import RequirementsDB
from requirements_tool.utils.report_generator import ReportWriter
import os
from pathlib import Path
from robot.api import ExecutionResult
from typing import Optional

from rich.traceback import install
install(show_locals=True)

db = RequirementsDB()

def add():
    """Add a new requirement interactively."""
    description = typer.prompt("Description")
    req_type = typer.prompt("Type [functional, non-functional, constraint]")
    domain = typer.prompt("Domain [e.g., logging, ble, data-processing]")

    db.add_requirement(description=description, req_type=req_type, domain=domain)

def remove(req_id: int):
    """Remove a requirement by ID and renumber the rest."""
    if req_id < 1:
        typer.echo("Requirement ID must be greater than 0.")
        raise typer.Exit(code=1)

    db.rm(req_id)

def update(req_id: int, field: str = None, value: str = None):
    """Update a requirement by REQ ID. Interactive or field-based."""
    db.update_requirement(req_id, field, value)

def show_requirements(req_type: Optional[str] = None, domain: Optional[str] = None):
    """Show requirements with optional filtering by type/domain."""
    db.show_requirements(req_type, domain)

def show_types():
    """Show all unique types."""
    db.show_characteristic("type")

def show_domains():
    """Show all unique domains."""
    db.show_characteristic("domain")

def trace(
    output: str = typer.Option("traceability.csv", help="Output report filename"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    fmt: str = typer.Option("csv", help="Output format: console, csv, json"),
    update_db: bool = typer.Option(False, help="Update linked_tests field in database"),
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    if not Path(robot_output).exists():
        typer.echo(f"Robot output file '{robot_output}' not found.")
        raise typer.Exit()

    result = ExecutionResult(robot_output)

    req_map = {}

    root_source = result.suite.source
    get_filename = lambda root, src: os.path.basename(src or root)

    for suite in result.suite.suites:
        suite_filename = get_filename(root_source, suite.source)
        for test in suite.tests:
            for tag in test.tags:
                if tag.startswith("REQ-"):
                    req_map.setdefault(tag, []).append((suite_filename, test.name, test.status))

    req_dict = db.get_requirements()

    report = []

    for req_id, uuid in req_dict.items():
        test_links = req_map.get(req_id, [])
        if test_links:
            suite_srcs = {src for src, _, _ in test_links}
            linked = [name for _, name, _ in test_links]
            statuses = [status for _, _, status in test_links]
            status = "FAILED" if "FAIL" in statuses else "PASSED"
        else:
            suite_srcs = set()
            linked = []
            status = "NOT TESTED"

        if update_db:
            db.link_tests(tests, uuid)

        for test_name in linked or [""]:
            report.append({
                "REQ-ID": req_id,
                "suite": ", ".join(sorted(suite_srcs)) if suite_srcs else "",
                "linked_test": test_name,
                "STATUS": status if test_name else "NOT TESTED",
            })

    writer = ReportWriter(report)
    writer.write(fmt, output)
