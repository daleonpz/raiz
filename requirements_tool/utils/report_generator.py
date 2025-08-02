# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0
import csv
import json
from typing import List, Dict
from rich.table import Table
from rich.console import Console
from pathlib import Path

console = Console()

class ReportWriter:
    def __init__(self, report_data ):
        self.report_data = report_data
        self.fields = ["REQ-ID", "suite", "linked_test", "STATUS"]
        self.console = Console()

    @staticmethod
    # [ [ header1, header2, header3 ], [ row1col1, row1col2, row1col3 ], ... ]
    def print_table_console(data: List, title: str = "Report", with_title: bool = True):
        """Prints a table to the console using Rich."""

        if with_title:
            table = Table(title=title, show_header=True, header_style="bold magenta")
        else:
            table = Table(show_header=True, header_style="bold magenta")

        if not data:
            print("No data to display.")
            return

        headers = data[0]
        for header in headers:
            table.add_column(header, style="cyan")

        for row in data[1:]:
            table.add_row(*row)

        console.print(table)

    @staticmethod
    def print_table_json(data: List):
        """Prints a table to the console in JSON format."""
        console.print_json(data=data, indent=2)

    def write_console(self, domain: str = None, req_type: str = None, detail: bool = False):
        """Pretty-prints the report to the console using Rich."""

        coverage_table = []
        coverage_table.append([
            "Total Requirements",
            "Tested Requirements",
            "Pass Rate",
            "Coverage",])

        coverage_table.append([
            str(self.report_data["coverage"]["total_requirements"]),
            str(self.report_data["coverage"]["tested_requirements"]),
            str(self.report_data["coverage"]["pass_rate"]),
            str(self.report_data["coverage"]["coverage_rate"])
        ])

        self.print_table_console(coverage_table, title="Coverage Summary", with_title=True)

        traceability_report = []
        traceability_report.append(self.fields)

        req_report = list(self.report_data["report"].values())

        for req_id, data in self.report_data["report"].items():
            # sometimes the values are [] and sometimes they are not
            test_results = data.get("test_results", [])
            for test in test_results:
                suite, test_name, status = test
                traceability_report.append([
                    req_id,
                    suite if suite else "-",
                    test_name if test_name else "-",
                    status if status else "-"
                ])

        self.print_table_console(traceability_report, title="Requirement Traceability Report", with_title=True)

        if detail:
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

