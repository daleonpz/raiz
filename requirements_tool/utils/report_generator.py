# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0
import csv
import json
from typing import List, Dict
from rich.table import Table
from rich.console import Console
from pathlib import Path


class ReportWriter:
    def __init__(self, report_data: List[Dict]):
        self.report_data = report_data
        self.fields = ["REQ-ID", "suite", "linked_test", "STATUS"]
        self.console = Console()

    def write_console(self):
        """Pretty-prints the report to the console using Rich."""
        table = Table(title="Requirement Traceability Report")

        for field in self.fields:
            table.add_column(field, style="bold")

        for row in self.report_data:
            table.add_row(
                row.get("REQ-ID", ""),
                row.get("suite", ""),
                row.get("linked_test", ""),
                row.get("STATUS", "")
            )

        self.console.print(table)

    def write_csv(self, output_path: str):
        """Writes the report to a CSV file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(self.report_data)

    def write_json(self, output_path: str):
        """Writes the report to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.report_data, f, indent=4)

    def write(self, format: str, output_path: str = ""):
        """Dispatch writer based on format."""
        if format == "console":
            self.write_console()
        elif format == "csv":
            self.write_csv(output_path)
            self.console.print(f"[green]Traceability CSV report saved to {output_path}[/green]")
        elif format == "json":
            self.write_json(output_path)
            self.console.print(f"[green]Traceability JSON report saved to {output_path}[/green]")
        else:
            self.console.print(f"[red]Unsupported format: {format}[/red]")

