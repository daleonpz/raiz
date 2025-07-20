# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
import sqlite3
import uuid
import yaml
from pathlib import Path
from typing import Optional
import logging
from robot.api import ExecutionResult
import csv
import os
import json
from datetime import datetime
import rich
from rich.console import Console
from rich.table import Table
from collections import defaultdict

# TODO: 
# - clean code, split into modules
# - add 'reports' folder
# - make it professional, readme, github actions, etc.
# - build package with setup.py 

app = typer.Typer()
list_app = typer.Typer()
sync_app = typer.Typer()
app.add_typer(list_app, name="list", help="List requirements, types, or domains")
app.add_typer(sync_app, name="sync", help="Sync requirements with YAML file")

console = Console()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

REQ_CACHE_DIR = Path(".req_cache")
REQ_CACHE_DIR.mkdir(exist_ok=True)
DB_FILE = REQ_CACHE_DIR / "requirements.db"
REQS_DIR = Path("requirements")
REQS_DIR.mkdir(exist_ok=True)
REQ_FILE = REQS_DIR / "requirements.yaml"

def db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            uuid TEXT PRIMARY KEY,
            seq_no INTEGER UNIQUE,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            domain TEXT NOT NULL,
            linked_tests TEXT DEFAULT ''
        )
        """)
        conn.commit()


def renumber_all():
    with db_conn() as conn:
        cur = conn.execute("SELECT uuid FROM requirements ORDER BY seq_no ASC")
        uuids = [row["uuid"] for row in cur.fetchall()]
        for i, uid in enumerate(uuids, start=1):
            conn.execute("UPDATE requirements SET seq_no = ? WHERE uuid = ?", (i, uid))
        conn.commit()

########## Commands ##########
@app.command()
def add():
    """Add a new requirement."""
    init_db()
    description = typer.prompt("Description")
    req_type = typer.prompt("Type [functional, non-functional, constraint]")
    domain = typer.prompt("Domain [e.g., logging, ble, data-processing]")

    with db_conn() as conn:
        cur = conn.execute("SELECT MAX(seq_no) FROM requirements")
        max_seq = cur.fetchone()[0] or 0
        seq_no = max_seq + 1
        conn.execute(
            "INSERT INTO requirements (uuid, seq_no, description, type, domain) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), seq_no, description, req_type, domain)
        )
        conn.commit()

    console.print(f"[bold green]REQ-{seq_no:03} added[/bold green]")


@app.command()
def rm(seq_no: int):
    """Remove a requirement by sequence number and renumber the rest."""
    init_db()
    with db_conn() as conn:
        conn.execute("DELETE FROM requirements WHERE seq_no = ?", (seq_no,))
        conn.commit()
    renumber_all()
    console.print(f"[bold red]REQ-{seq_no:03} removed and renumbered[/bold red]")

@list_app.command("all")
def list_all(
    type: Optional[str] = typer.Option(None, help="Filter by type"),
    domain: Optional[str] = typer.Option(None, help="Filter by domain"),
    json: Optional[bool] = typer.Option(False, help="Output in JSON format"),
):
    """List all requirements, with optional filters."""
    init_db()
    query = "SELECT * FROM requirements WHERE 1=1"
    params = []

    if type:
        query += " AND type = ?"
        params.append(type)
    if domain:
        query += " AND domain = ?"
        params.append(domain)

    with db_conn() as conn:
        cur = conn.execute(query, params)

        if not json:
            req_table = Table(show_header=True, header_style="bold magenta")
            req_table.add_column("REQ-ID", style="cyan")
            req_table.add_column("Description", style="white")
            req_table.add_column("Type", style="green")
            req_table.add_column("Domain", style="yellow")

            for row in cur.fetchall():
                req_table.add_row(
                    f"REQ-{row['seq_no']:03}",
                    row["description"],
                    row["type"],
                    row["domain"]
                )

            console.print(req_table)
        else:
            requirements = []
            for row in cur.fetchall():
                requirements.append({
                    "id": f"REQ-{row['seq_no']:03}",
                    "uuid": row["uuid"],
                    "description": row["description"],
                    "type": row["type"],
                    "domain": row["domain"],
                    "linked_tests": row["linked_tests"].split(",") if row["linked_tests"] else [],
                })
            console.print_json(data=requirements, indent=2)


@list_app.command("types")
def list_types():
    """List all unique requirement types."""
    init_db()
    with db_conn() as conn:
        types_table = Table(show_header=True, header_style="bold magenta")
        cur = conn.execute("SELECT DISTINCT type FROM requirements")
        types = sorted(row["type"] for row in cur.fetchall())
        types_table.add_column("Requirement Types", style="cyan")
        for t in types:
            types_table.add_row(t)
        console.print(types_table)

@list_app.command("domains")
def list_domains():
    """List all unique requirement domains."""
    init_db()
    with db_conn() as conn:
        domains_table = Table(show_header=True, header_style="bold magenta")
        cur = conn.execute("SELECT DISTINCT domain FROM requirements")
        domains = sorted(row["domain"] for row in cur.fetchall())
        domains_table.add_column("Requirement Domains", style="cyan")
        for d in domains:
            domains_table.add_row(d)
        console.print(domains_table)

@sync_app.command("to-yaml")
def sync_to_yaml(
    file: Optional[Path] = typer.Option(REQ_FILE, help="Path to output YAML file")
):
    """Dump current SQLite requirements to YAML."""
    init_db()
    with db_conn() as conn:
        cur = conn.execute("SELECT * FROM requirements ORDER BY seq_no ASC")
        reqs = []
        for row in cur.fetchall():
            reqs.append({
                "id": f"REQ-{row['seq_no']:03}",
                "uuid": row["uuid"],
                "description": row["description"],
                "type": row["type"],
                "domain": row["domain"],
                "linked_tests": row["linked_tests"].split(",") if row["linked_tests"] else [],
            })

    if file:
        REQ_FILE = Path(file)
        console.print(f"[bold yellow]Using provided YAML file: {REQ_FILE}[/bold yellow]")

    with open(REQ_FILE, "w") as f:
        yaml.dump(reqs, f)

    console.print(f"[bold green]Exported {len(reqs)} requirements to {REQ_FILE}[/bold green]")

@sync_app.command("from-yaml")
def sync_from_yaml(
    file: Optional[Path] = typer.Option(REQ_FILE, help="Path to YAML file with requirements")
):
    """Import requirements from YAML into SQLite (overwrites DB)."""
    if file:
        REQ_FILE = Path(file)
        console.print(f"[bold yellow]Using provided YAML file: {REQ_FILE}[/bold yellow]")

    if not REQ_FILE.exists():
        console.print(f"[bold red]Error: {REQ_FILE} not found.[/bold red]")
        raise typer.Exit()

    with open(REQ_FILE, "r") as f:
        reqs = yaml.safe_load(f)

    init_db()
    with db_conn() as conn:
        conn.execute("DELETE FROM requirements")
        for idx, req in enumerate(reqs, start=1):
            conn.execute(
                "INSERT INTO requirements (uuid, seq_no, description, type, domain, linked_tests) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    req["uuid"],
                    idx,
                    req["description"],
                    req["type"],
                    req["domain"],
                    ",".join(req.get("linked_tests", []))
                )
            )
        conn.commit()
    console.print(f"[bold green]Requirements imported from {REQ_FILE}[/bold green]")

@app.command()
def update(
    seq_no: int,
    field: Optional[str] = typer.Argument(None),
    new_value: Optional[str] = typer.Argument(None),
):
    """Update a requirement interactively or by field."""
    init_db()

    with db_conn() as conn:
        cur = conn.execute("SELECT * FROM requirements WHERE seq_no = ?", (seq_no,))
        row = cur.fetchone()
        if not row:
            console.print("[bold red]Requirement REQ-{seq_no:03} not found.[/bold red]")
            raise typer.Exit()

        if field:
            if field not in {"description", "type", "domain"}:
                console.print("[bold red]Invalid field. Only 'description', 'type', and 'domain' can be updated.[/bold red]")
                raise typer.Exit()
            conn.execute(f"UPDATE requirements SET {field} = ? WHERE seq_no = ?", (new_value, seq_no))
            conn.commit()
            console.print(f"[bold green]Updated REQ-{seq_no:03}: set {field} to '{new_value}'[/bold green]")
        else:
            # Interactive prompt
            console.print(f"[bold yellow]Updating REQ-{seq_no:03} interactively...[/bold yellow]")
            description = typer.prompt("Description", default=row["description"])
            req_type = typer.prompt("Type [functional, non-functional, constraint]", default=row["type"])
            domain = typer.prompt("Domain [e.g., logging, ble, data-processing]", default=row["domain"])

            conn.execute("""
                UPDATE requirements
                SET description = ?, type = ?, domain = ?
                WHERE seq_no = ?
            """, (description, req_type, domain, seq_no))
            conn.commit()
            console.print(f"[bold green]REQ-{seq_no:03} updated successfully![/bold green]")


@app.command()
def trace(
    output: str = typer.Option("traceability", help="Output report to console or a file (CSV or JSON)"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    format: str = typer.Option("console", help="Output format: console, csv or json"),
    update_db: bool = typer.Option(False, help="Update SQLite with linked_tests"),
    domain: Optional[str] = typer.Option(None, help="Filter by domain"),
    type: Optional[str] = typer.Option(None, help="Filter by requirement type"),
    detail: bool = typer.Option(False, help="Show detailed trace report (only in console)")
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    init_db()

    if not Path(robot_output).exists():
        console.print(f"[bold red]Robot output file {robot_output} not found.[/bold red]")
        raise typer.Exit()

    result = ExecutionResult(robot_output)

    # Gather test → REQ links
    req_map = defaultdict(list)
    orphan_tests = []

    root_source = result.suite.source
    get_filename = lambda root, suite_src : os.path.basename(suite_src)

    for suite in result.suite.suites:
        suite_filename = get_filename(root_source, suite.source)
        for test in suite.tests:
            for tag in test.tags:
                if tag.startswith("REQ-"):
                    req_map[tag].append((suite_filename, test.name, test.status))

    with db_conn() as conn:
        cur = conn.execute("SELECT uuid, seq_no, type, domain FROM requirements")
        reqs = cur.fetchall()
        req_dict = {f"REQ-{row['seq_no']:03}": row for row in reqs}

    req_report = defaultdict(dict)
    total_req = 0
    num_passed = num_failed = 0

    with db_conn() as conn:
        for req_id, data in req_dict.items():
            if (type and data["type"] != type) or (domain and data["domain"] != domain):
                continue
            total_req += 1

            uuid = data["uuid"]
            if req_id in req_map:
                suite_src = [s for s, _, _ in req_map[req_id]]
                linked = [t for _, t, _ in req_map[req_id]]
                statuses = [s for _, _, s in req_map[req_id]]
                overall = "FAILED" if "FAIL" in statuses else "PASSED"
                if overall == "PASSED":
                    num_passed += 1
                else:
                    num_failed += 1
            else:
                suite_src, linked, overall = [], [], "NOT TESTED"

            if update_db:
                conn.execute("UPDATE requirements SET linked_tests = ? WHERE uuid = ?", (",".join(linked), uuid))

            for test_name in linked or [""]:
                req_report[uuid] = {
                    "REQ-ID": req_id,
                    "STATUS": overall if test_name else "NOT TESTED",
                    "suite": ", ".join(suite_src) if isinstance(suite_src, list) else suite_src,
                    "linked_test": test_name,
                }

        if detail:
            cur = conn.execute("SELECT DISTINCT domain FROM requirements")
            domains = sorted(row["domain"] for row in cur.fetchall())
    
            cur = conn.execute("SELECT DISTINCT type FROM requirements")
            types = sorted(row["type"] for row in cur.fetchall())

            domain_stats = defaultdict(lambda: {"total": 0, "tested": 0, "passed": 0})
            type_stats = defaultdict(lambda: {"total": 0, "tested": 0, "passed": 0})

            for domain in domains:
                cur = conn.execute( "SELECT COUNT(*) FROM requirements WHERE domain = ?", (domain,))
                domain_stats[domain]["total"] = cur.fetchone()[0]

                cur = conn.execute(
                    "SELECT uuid FROM requirements WHERE domain = ? AND linked_tests != ''",
                    (domain,)
                )
                fetched_data = cur.fetchall()
                domain_stats[domain]["tested"] = len(fetched_data)

                dom_passed = [ req_report[row["uuid"]]["STATUS"] for row in fetched_data if row["uuid"] in req_report ]
                logging.debug(f"Domain {domain} passed statuses: {dom_passed}")
                domain_stats[domain]["passed"] = (dom_passed.count("PASSED") / len(dom_passed) * 100) if dom_passed else 0

            for typ in types:
                cur = conn.execute("SELECT COUNT(*) FROM requirements WHERE type = ?", (typ,))
                type_stats[typ]["total"] = cur.fetchone()[0]

                cur = conn.execute(
                    "SELECT uuid FROM requirements WHERE type = ? AND linked_tests != ''",
                    (typ,)
                )
                fetched_data = cur.fetchall()
                type_stats[typ]["tested"] = len(fetched_data)

                typ_passed = [ req_report[row["uuid"]]["STATUS"] for row in fetched_data if row["uuid"] in req_report ]
                logging.debug(f"Type {typ} passed statuses: {typ_passed}")
                type_stats[typ]["passed"] = (typ_passed.count("PASSED") / len(typ_passed) * 100) if typ_passed else 0
    
        if update_db:
            conn.commit()

    # Coverage
    total_tests = num_passed + num_failed
    coverage = (total_tests / total_req * 100) if total_req else 0
    pass_rate = (num_passed / total_tests * 100) if total_tests else 0

    report = {
        "timestamp": datetime.now().isoformat(),
        "coverage": {
            "total_requirements": total_req,
            "total_tests": total_tests,
            "passed_tests": pass_rate,
            "ignored_tests": total_req - total_tests,
            "coverage_percentage": coverage,
        },
        "report": req_report,
    }

    if detail:
        detailed = defaultdict(dict)
        detailed["domains"] = domain_stats
        detailed["types"] = type_stats
        report["detail_coverage"] = detailed

    # Output
    if format == "console":
        generate_console_report(report)
    elif format == "csv":
        generate_csv_report(report, output)
        console.print(f"[green]Traceability CSV report saved to {output}[/green]")
    elif format == "json":
        generate_json_report(report, output)
        console.print(f"[green]Traceability JSON report saved to {output}[/green]")
    else:
        console.print("[bold red]Invalid format. Use console, csv, or json.[/bold red]")


## Generate reports in different formats
def generate_console_report(report: dict):
    """Generate a console report from traceability data."""

    console = Console()
    console.print(f"[blink][bold green]Traceability Report - {report['timestamp']}[/blink][/bold green]", justify="center")

    # --- Requirements Coverage Summary ---
    cov_table = Table(title="Requirements Coverage Summary", show_header=True, header_style="bold blue")
    cov_table.add_column("Total Requirements", style="dim")
    cov_table.add_column("Tested Requirements", style="dim")
    cov_table.add_column("Passed Tests (%)", style="green")
    cov_table.add_column("Ignored Tests", style="yellow")
    cov_table.add_column("Requirements Covered (%)", style="bold")

    cov = report["coverage"]
    cov_table.add_row(
        str(cov["total_requirements"]),
        str(cov["total_tests"]),
        f"{cov['passed_tests']:.2f}%",
        str(cov["ignored_tests"]),
        f"{cov['coverage_percentage']:.2f}%",
    )
    console.print(cov_table)

    # --- Traceability Table ---
    trace_table = Table(title="Traceability Report", show_header=True, header_style="bold magenta")
    trace_table.add_column("REQ-ID", style="cyan", no_wrap=True)
    trace_table.add_column("Status", style="green")
    trace_table.add_column("Suite", style="yellow")
    trace_table.add_column("Linked Test", style="blue")

    req_report = list(report["report"].values())
    for row in req_report:
        trace_table.add_row(
            row["REQ-ID"],
            row["STATUS"],
            row["suite"] or "-",
            row["linked_test"] or "-"
        )
    console.print(trace_table)

    # --- Detailed Domain/Type Coverage ---
    if "detail_coverage" in report:
        detail_table = Table(title="Coverage per Domain", header_style="bold cyan")
        detail_table.add_column("Domain", style="magenta")
        detail_table.add_column("Total REQs", justify="right")
        detail_table.add_column("Tested", justify="right")
        detail_table.add_column("Passed %", justify="right")
        detail_table.add_column("Coverage %", justify="right")

        for domain, stats in report["detail_coverage"]["domains"].items():
            coverage_pct = (stats["tested"] / stats["total"] * 100) if stats["total"] else 0
            detail_table.add_row(
                domain,
                str(stats["total"]),
                str(stats["tested"]),
                str(stats["passed"]),
                f"{coverage_pct:.2f}%"
            )
        console.print(detail_table)

        type_table = Table(title="Coverage per Type", header_style="bold cyan")
        type_table.add_column("Type", style="magenta")
        type_table.add_column("Total REQs", justify="right")
        type_table.add_column("Tested", justify="right")
        type_table.add_column("Passed %", justify="right")
        type_table.add_column("Coverage %", justify="right")
        for typ, stats in report["detail_coverage"]["types"].items():
            coverage_pct = (stats["tested"] / stats["total"] * 100) if stats["total"] else 0
            type_table.add_row(
                typ,
                str(stats["total"]),
                str(stats["tested"]),
                str(stats["passed"]),
                f"{coverage_pct:.2f}%"
            )
        console.print(type_table)


def generate_csv_report(report, output):
    """Generate a CSV report from traceability data."""
    output = output if output.endswith(".csv") else f"{output}.csv"

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["REQ-ID", "STATUS", "suite", "linked_test"])
        writer.writeheader()
        req_report = list(report["report"].values())
        for row in req_report:
            writer.writerow(row)

def generate_json_report(report, output):
    """Generate a JSON report from traceability data."""
    output = output if output.endswith(".json") else f"{output}.json"

    with open(output, "w") as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":
    app()

