# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
import typer
from robot.api import ExecutionResult
from requirements_tool.utils.database import RequirementsDB
from requirements_tool.utils.report_generator import ReportWriter
from rich.console import Console

from rich.traceback import install
install(show_locals=True)

console = Console()

def trace(
    output: str = typer.Option("traceability.csv", help="Output report filename"),
    robot_output: str = typer.Option("output.xml", help="Path to Robot Framework output.xml"),
    fmt: str = typer.Option("csv", help="Output format: console, csv, json"),
    update_db: bool = typer.Option(False, help="Update linked_tests field in database"),
):
    """
    Generate traceability report linking REQ-IDs to Robot tests.
    """
    db = RequirementsDB()

    if not Path(robot_output).exists():
        console.print(f"[red]Robot output file '{robot_output}' not found.[/red]")
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

    # Load requirements from DB
    with db_conn() as conn:
        cur = conn.execute("SELECT uuid, seq_no FROM requirements")
        req_dict = {f"REQ-{row['seq_no']:03}": row["uuid"] for row in cur.fetchall()}

    report = []
    with db_conn() as conn:
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
                conn.execute(
                    "UPDATE requirements SET linked_tests = ? WHERE uuid = ?",
                    (",".join(linked), uuid),
                )

            for test_name in linked or [""]:
                report.append({
                    "REQ-ID": req_id,
                    "suite": ", ".join(sorted(suite_srcs)) if suite_srcs else "",
                    "linked_test": test_name,
                    "STATUS": status if test_name else "NOT TESTED",
                })

        if update_db:
            conn.commit()
    
    writer = ReportWriter(report)
    writer.write(fmt, output)

#     if fmt == "console":
#         generate_console_report(report)
#     elif fmt == "csv":
#         generate_csv_report(report, output)
#         console.print(f"[green]Traceability CSV report saved to {output}[/green]")
#     elif fmt == "json":
#         generate_json_report(report, output)
#         console.print(f"[green]Traceability JSON report saved to {output}[/green]")
#     else:
#         console.print("[bold red]Invalid format. Use console, csv, or json.[/bold red]")
# 
