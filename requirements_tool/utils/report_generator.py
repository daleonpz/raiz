# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0
import json
from rich.table import Table
from rich.console import Console
from pathlib import Path

from typing import List, Optional, Callable, Union
from rich.style import Style

console = Console()

class ReportWriter:
    def __init__(self, report_data ):
        self.report_data = report_data
        self.fields = ["REQ-ID", "Status", "suite", "linked_test"]
        self.console = Console()

    @staticmethod
    # [ [ header1, header2, header3 ], [ row1col1, row1col2, row1col3 ], ... ]
    def print_table_console(data: List[List[str]], 
                            title: str = "Report", 
                            with_title: bool = True, 
                            cell_styles: Optional[dict] = {},
                            row_style_cb: Optional[Callable[[List[str], int], Union[str, Style, None]]] = None
                            ):
        """Prints a table to the console using Rich."""

        table = Table(title=title if with_title else None, show_header=True, header_style="bold magenta")

        if not data:
            print("No data to display.")
            return

        headers = data[0]
        for header in headers:
            table.add_column(header, style="cyan")
        data_rows = data[1:] if len(data) > 1 else []

        # Add rows with styling
        for row_idx, row in enumerate(data_rows):
            # Prepare styled row cells
            styled_row = []
            for cell in row:
                style = cell_styles.get(cell, None)
                styled_cell = f"[{style}]{cell}[/]" if style else cell
                styled_row.append(styled_cell)

            row_style = None
            if row_style_cb:
                row_style = row_style_cb(row, row_idx)

            table.add_row(*styled_row, style=row_style)

        console.print(table)

    @staticmethod
    def print_table_json(data: List):
        """Prints a table to the console in JSON format."""
        console.print_json(data=data, indent=2)

    def write_console(self, domain: str = None, req_type: str = None, detail: bool = False):
        """Pretty-prints the report to the console using Rich."""

        console.print(f"[blink][bold green]Traceability Report - {self.report_data['timestamp']}[/blink][/bold green]", justify="center")

        coverage_table = []
        coverage_table.append([
            "Total Requirements",
            "Tested Requirements",
            "Pass Rate",
            "Coverage",])

        if domain or req_type:
            print(f"Filtering coverage for domain: {domain}, type: {req_type}")
            if domain:
                coverage = self.report_data["detailed_report"]["domains"].get(domain, {})
            elif req_type:
                coverage = self.report_data["detailed_report"]["types"].get(req_type, {})
        else :
            coverage = self.report_data["coverage"]

        coverage_table.append([
            str(coverage.get("total_requirements", 0)),
            str(coverage.get("tested_requirements", 0)),
            f"{coverage.get('pass_rate', 0)}%",
            f"{coverage.get('coverage_rate', 0)}%"
        ])

        self.print_table_console(coverage_table, title="Coverage Summary", with_title=True)

        traceability_report = []
        traceability_report.append(self.fields)

        if domain or req_type:
            filtered_report = {}
            for req_id, data in self.report_data["report"].items():
                if (domain and data.get("domain") == domain) or (req_type and data.get("type") == req_type):
                    filtered_report[req_id] = data
            self.report_data["report"] = filtered_report

        for req_id, data in self.report_data["report"].items():
            # sometimes the values are [] and sometimes they are not
            test_results = data.get("test_results", [])
            for test in test_results:
                suite, test_name, status = test
                traceability_report.append([
                    req_id,
                    status if status else "-",
                    suite if suite else "-",
                    test_name if test_name else "-",
                ])

            ## if test_results is empty, we still want to show the requirement
            if not test_results:
                traceability_report.append([
                    req_id,
                    "NOT TESTED",
                    "-",
                    "-",
                ])

        # Define cell styles
        cell_styles = {
            "FAIL": Style(color="white", blink=True, bold=True),
            "PASS": "green",
            "NOT TESTED": "yellow",
        }

        # Define row style callback (e.g., yellow background for rows where Status is "FAIL")
        def row_style_callback(row: List[str], row_idx: int) -> Optional[str]:
            return "on red" if row[1] == "FAIL" else None

        self.print_table_console(traceability_report, title="Requirement Traceability Report", with_title=True, 
                                 cell_styles=cell_styles, row_style_cb=row_style_callback)

        if detail and not (domain or req_type):
            detailed_stats = self.report_data.get("detailed_report", {})
            domain_tables = [["Domain", "Total Requirements", "Number of Tested Requirements", "Pass Rate", "Coverage Rate"]]
            for domain, val in detailed_stats["domains"].items():
                domain_tables.append([
                    domain,
                    str(val["total_requirements"]),
                    str(val["tested_requirements"]),
                    f"{val['pass_rate']}%",
                    f"{val['coverage_rate']}%"
                ])

                type_tables= [["Type", "Total Requirements", "Number of Tested Requirements", "Pass Rate", "Coverage Rate"]]
                for typ, val in detailed_stats["types"].items():
                    type_tables.append([
                        typ,
                        str(val["total_requirements"]),
                        str(val["tested_requirements"]),
                        f"{val['pass_rate']}%",
                        f"{val['coverage_rate']}%"
                    ])

            self.print_table_console(domain_tables, title="Domain Statistics", with_title=True)
            self.print_table_console(type_tables, title="Type Statistics", with_title=True)

    def write_json(self, output_path: str, 
                   domain: str = None, 
                   req_type: str = None, 
                   detail: bool = False):
        """Writes the report to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.report_data, f, indent=4)

    def write(self, fmt: str,
              output_path: str = "",
              domain: str = None,
              req_type: str = None,
              detail: bool = False):
        """Dispatch writer based on fmt."""
        output_path = output_path + "." + fmt
        if fmt == "console":
            self.write_console(domain=domain, req_type=req_type, detail=detail)
        elif fmt == "json":
            self.write_json(output_path)
            self.console.print(f"[green]Traceability JSON report saved to {output_path}[/green]")
        else:
            self.console.print(f"[red]Unsupported fmt: {fmt}[/red]")

