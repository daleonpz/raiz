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

app = typer.Typer()
list_app = typer.Typer()
sync_app = typer.Typer()
app.add_typer(list_app, name="list", help="List requirements, types, or domains")
app.add_typer(sync_app, name="sync", help="Sync requirements with YAML file")

    
console = Console()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_FILE = "requirements.db"
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
def sync_to_yaml():
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

    with open(REQ_FILE, "w") as f:
        yaml.dump(reqs, f)

    console.print(f"[bold green]Exported {len(reqs)} requirements to {REQ_FILE}[/bold green]")

@sync_app.command("from-yaml")
def sync_from_yaml():
    """Import requirements from YAML into SQLite (overwrites DB)."""
    if not REQ_FILE.exists():
        console.print("[bold red]Error: requirements.yaml not found.[/bold red]")
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


#TODO: 
# Tests: what if i implement a test without a REQ-ID?
# filter trace by type, domain, status
@app.command()
def trace(
    output: str = typer.Option("traceability", help="Output report to the console or a file (CSV or JSON)"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    format: str = typer.Option("console", help="Output format: console, csv or json"),
    update_db: bool = typer.Option(False, help="Do not update SQLite linked_tests field")
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    init_db()


    if not Path(robot_output).exists():
        console.print(f"[bold red]Robot output file {robot_output} not found.[/bold red]")
        raise typer.Exit()

    result = ExecutionResult(robot_output)

    # Map: REQ-ID → list of (suite file name, test name, status)
    req_map = {}

    root_source = result.suite.source
    get_filename = lambda root, suite_src : os.path.basename(suite_src)

    for suite in result.suite.suites:
        suite_filename = get_filename(root_source, suite.source)
        for test in suite.tests:
            for tag in test.tags:
                if tag.startswith("REQ-"):
                    if tag not in req_map:
                        req_map[tag] = []
                    logging.debug(f"Linking {tag} to test {test.name} with status {test.status} from suite {suite_filename}")
                    req_map[tag].append((suite_filename, test.name, test.status))


    # Load existing requirements from DB
    with db_conn() as conn:
        cur = conn.execute("SELECT uuid, seq_no FROM requirements")
        req_dict = {f"REQ-{row['seq_no']:03}": row["uuid"] for row in cur.fetchall()}

    rows = []

    total_req = len(req_dict)
    num_fail_test = 0
    num_passed_test = 0
    num_ignored_test = 0

    with db_conn() as conn:
        for req_id, uuid in req_dict.items():
            if req_id in req_map:
                suite_src = [ src for src, _, _ in req_map[req_id] ]
                linked = [name for _, name, _ in req_map[req_id]]
                statuses = [status for _, _, status in req_map[req_id]]
                overall_status = "FAILED" if "FAIL" in statuses else "PASSED"
                if overall_status == "PASSED":
                    num_passed_test += 1
                elif overall_status == "FAILED":
                    num_fail_test += 1
                else:
                    num_ignored_test += 1
            else:
                suite_src = []
                linked = []
                overall_status = "NOT TESTED"

            if update_db:
                conn.execute("UPDATE requirements SET linked_tests = ? WHERE uuid = ?",
                             (",".join(linked), uuid))

            for test_name in linked or [""]:
                rows.append({
                    "REQ-ID": req_id,
                    "STATUS": overall_status if test_name else "NOT TESTED",
                    "suite": ", ".join(suite_src) if isinstance(suite_src, list) else suite_src,
                    "linked_test": test_name,
                })

        if update_db:
            conn.commit()

    # Coverage
    total_tests = num_passed_test + num_fail_test + num_ignored_test
    coverage = (num_passed_test + num_fail_test) / total_req * 100 if total_req > 0 else 0
    percentage_passed = num_passed_test / total_tests * 100 if total_tests > 0 else 0

    cov_report = {
        "total_requirements": total_req,
        "total_tests": total_tests,
        "passed_tests": percentage_passed,
        "ignored_tests": num_ignored_test,
        "coverage_percentage": coverage,
    }

    report = {
        "timestamp": datetime.now().isoformat(),
        "coverage": cov_report,
        "report": rows,
    }

    if format == "console":
       generate_console_report(report)
    elif format == "csv":
        generate_csv_report(report, output)
        console.print(f"[bold green]Traceability CSV report saved to {output}[/bold green]")
    elif format == "json":
        generate_json_report(report, output)
        console.print(f"[bold green]Traceability JSON report saved to {output}[/bold green]")
    else:
        console.print("[bold red]Invalid format. Use 'console', 'csv', or 'json'.[/bold red]")

## Generate reports in different formats
def generate_csv_report(report, output):
    """Generate a CSV report from traceability data."""
    output = output if output.endswith(".csv") else f"{output}.csv"

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["REQ-ID", "STATUS", "suite", "linked_test"])
        writer.writeheader()
        for row in report["report"]:
            writer.writerow(row)

def generate_json_report(report, output):
    """Generate a JSON report from traceability data."""
    output = output if output.endswith(".json") else f"{output}.json"

    with open(output, "w") as f:
        json.dump(report, f, indent=4)

def generate_console_report(report):
    """Generate a console report from traceability data."""

    console.print("[blink][bold green]Traceability Report - " + report['timestamp'] + "[/blink][/bold green]", justify="center")

    cov_table = Table(title="Requirements Coverage Summary", show_header=True, header_style="bold blue")
    cov_table.add_column("Total Requirements", style="dim")
    cov_table.add_column("Total Tests", style="dim")
    cov_table.add_column("Passed Tests (%)", style="green")
    cov_table.add_column("Ignored Tests", style="yellow")
    cov_table.add_column("Req. Coverage (%)", style="bold")
    cov_table.add_row(
        str(report["coverage"]["total_requirements"]),
        str(report["coverage"]["total_tests"]),
        f"{report['coverage']['passed_tests']:.2f}%",
        str(report["coverage"]["ignored_tests"]),
        f"{report['coverage']['coverage_percentage']:.2f}%",
            )

    console.print(cov_table)

    table = Table(title="Traceability Report", show_header=True, header_style="bold magenta")
    table.add_column("REQ-ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Suite", style="yellow")
    table.add_column("Linked Test", style="blue")
    for row in report["report"]:
        table.add_row(row["REQ-ID"], row["STATUS"], row["suite"], row["linked_test"] or "N/A")
    
    console.print(table)

if __name__ == "__main__":
    app()

