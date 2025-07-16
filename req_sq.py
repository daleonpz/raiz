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

app = typer.Typer()
list_app = typer.Typer()
sync_app = typer.Typer()
app.add_typer(list_app, name="list", help="List requirements, types, or domains")
app.add_typer(sync_app, name="sync", help="Sync requirements with YAML file")

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

    typer.echo("Requirement added.")


@app.command()
def rm(seq_no: int):
    """Remove a requirement by sequence number and renumber the rest."""
    init_db()
    with db_conn() as conn:
        conn.execute("DELETE FROM requirements WHERE seq_no = ?", (seq_no,))
        conn.commit()
    renumber_all()
    typer.echo(f"Removed REQ-{seq_no:03} and renumbered.")


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
        for row in cur.fetchall():
            typer.echo(f"REQ-{row['seq_no']:03}: {row['description']} [{row['type']}, {row['domain']}]")

@list_app.command("types")
def list_types():
    """List all unique requirement types."""
    init_db()
    with db_conn() as conn:
        cur = conn.execute("SELECT DISTINCT type FROM requirements")
        types = sorted(row["type"] for row in cur.fetchall())
        typer.echo("Types:")
        for t in types:
            typer.echo(f"- {t}")

@list_app.command("domains")
def list_domains():
    """List all unique requirement domains."""
    init_db()
    with db_conn() as conn:
        cur = conn.execute("SELECT DISTINCT domain FROM requirements")
        domains = sorted(row["domain"] for row in cur.fetchall())
        typer.echo("Domains:")
        for d in domains:
            typer.echo(f"- {d}")


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
    typer.echo(f"Exported {len(reqs)} requirements to {REQ_FILE}")


@sync_app.command("from-yaml")
def sync_from_yaml():
    """Import requirements from YAML into SQLite (overwrites DB)."""
    if not REQ_FILE.exists():
        typer.echo("requirements.yaml not found.")
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
    typer.echo(f"Imported {len(reqs)} requirements from {REQ_FILE}")


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
            typer.echo(f"Requirement REQ-{seq_no:03} not found.")
            raise typer.Exit()

        if field:
            if field not in {"description", "type", "domain"}:
                typer.echo("Only 'description', 'type', and 'domain' can be updated.")
                raise typer.Exit()
            conn.execute(f"UPDATE requirements SET {field} = ? WHERE seq_no = ?", (new_value, seq_no))
            conn.commit()
            typer.echo(f"Updated REQ-{seq_no:03}: set {field} to '{new_value}'")
        else:
            # Interactive prompt
            typer.echo(f"Updating REQ-{seq_no:03}")
            description = typer.prompt("Description", default=row["description"])
            req_type = typer.prompt("Type [functional, non-functional, constraint]", default=row["type"])
            domain = typer.prompt("Domain [e.g., logging, ble, data-processing]", default=row["domain"])

            conn.execute("""
                UPDATE requirements
                SET description = ?, type = ?, domain = ?
                WHERE seq_no = ?
            """, (description, req_type, domain, seq_no))
            conn.commit()
            typer.echo(f"Updated REQ-{seq_no:03}")


#TODO: 
# pimp the traceability report with more details, specially html
# show a more beautiful report with links to the tests
# typer.echo should print in a table format and with colors
# Tests: what if i implement a test without a REQ-ID?
# Remove: linked_tests from database, it is not needed anymore
@app.command()
def trace(
    output: str = typer.Option("traceability", help="Output report filename (CSV, JSON or HTML)"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    format: str = typer.Option("csv", help="Output format: csv, json or html"),
    update_db: bool = typer.Option(False, help="Do not update SQLite linked_tests field")
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    init_db()

    if not Path(robot_output).exists():
        typer.echo(f"Robot output file {robot_output} not found.")
        raise typer.Exit()

    result = ExecutionResult(robot_output)

    # Map: REQ-ID → list of (suite file name, test name, status)
    req_map = {}

    root_source = result.suite.source
    get_filename = lambda root, suite_src : os.path.basename(suite_src)

    logging.info(f"Root suite source: {root_source}")
    for suite in result.suite.suites:
        suite_filename = get_filename(root_source, suite.source)
        for test in suite.tests:
            for tag in test.tags:
                if tag.startswith("REQ-"):
                    if tag not in req_map:
                        req_map[tag] = []
                    logging.info(f"Linking {tag} to test {test.name} with status {test.status} from suite {suite_filename}")
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

    typer.echo(f"Total Requirements: {total_req}")
    typer.echo(f"Total Tests: {total_tests}")
    typer.echo(f"Passed Tests: {num_passed_test} ({percentage_passed:.2f}%)")
    typer.echo(f"Failed Tests: {num_fail_test}")
    typer.echo(f"Ignored Tests: {num_ignored_test}")
    typer.echo(f"Coverage: {coverage:.2f}%")

    # Output CSV
    if format == "csv":
        output = output if output.endswith(".csv") else f"{output}.csv"
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["REQ-ID", "STATUS", "suite", "linked_test"])
            writer.writeheader()
            writer.writerows(rows)
        typer.echo(f"Traceability CSV report saved to {output}")
    elif format == "json":
        output = output if output.endswith(".json") else f"{output}.json"
        with open(output, "w") as f:
            json.dump(rows, f, indent=4)
        typer.echo(f"Traceability JSON report saved to {output}")
    elif format == "html":
        output = output if output.endswith(".html") else f"{output}.html"
        generate_html_report(rows, output)
        typer.echo(f"Traceability HTML report saved to {output}")
    else:
        typer.echo("Invalid format. Use 'csv' or 'html'.")


def generate_html_report(rows, output):
    """Generate a simple HTML report from traceability data."""
    html_content = """
    <html>
    <head>
        <title>Traceability Report</title>
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Traceability Report</h1>
        <table>
            <tr>
                <th>REQ-ID</th>
                <th>Suite</th>
                <th>Linked Test</th>
                <th>Status</th>
            </tr>
    """
    for row in rows:
        html_content += f"""
            <tr>
                <td>{row['REQ-ID']}</td>
                <td>{row['STATUS']}</td>
                <td>{row['suite']}</td>
                <td>{row['linked_test']}</td>
            </tr>
        """
    html_content += """
        </table>
    </body>
    </html>
    """

    with open(output, "w") as f:
        f.write(html_content)


if __name__ == "__main__":
    app()

