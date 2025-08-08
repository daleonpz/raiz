# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

from raiz.utils.report_generator import ReportWriter

import sqlite3
from typing import Optional, List, Dict
import uuid
from pathlib import Path
from collections import defaultdict
import typer
from rich.console import Console
from rich.traceback import install
install(show_locals=True)

REQ_CACHE_DIR = Path(".req_cache")
REQ_CACHE_DIR.mkdir(exist_ok=True)
DB_PATH = REQ_CACHE_DIR / "requirements.db"

REQS_DIR = Path("requirements")
REQS_DIR.mkdir(exist_ok=True)
REQ_FILE = REQS_DIR / "requirements.yaml"

HEADER_STYLE = "bold magenta"
MAIN_COLUMN_STYLE = "cyan"

console = Console()

class Database:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.conn = None
        self.initialize()

    def initialize(self):
        """Initialize the database and create the requirements table if it doesn't exist."""
        with self as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS requirements (
                    uuid TEXT PRIMARY KEY,
                    seq_no INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    linked_tests TEXT DEFAULT ''
                )
            """)
            conn.commit()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

class RequirementsDB:
    def __init__(self, database: Optional[Database] = None):
        self.database = database or Database()

    def add_requirement(self,  description: str, req_type: str, domain: str):
        with self.database as conn:
            cur = conn.execute("SELECT MAX(seq_no) FROM requirements")
            max_seq = cur.fetchone()[0] or 0
            seq_no = max_seq + 1
            conn.execute(
                "INSERT INTO requirements (uuid, seq_no, description, type, domain) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), seq_no, description, req_type, domain)
            )
            conn.commit()

        console.print(f"[bold green]REQ-{seq_no:03} added[/bold green]")

    def rm(self, seq_no: int):
        """Remove a requirement by sequence number and renumber the rest."""
        with self.database as conn:
            conn.execute("DELETE FROM requirements WHERE seq_no = ?", (seq_no,))
            conn.commit()
            self.renumber_all()

        console.print(f"[bold red]REQ-{seq_no:03} removed[/bold red]")

    def renumber_all(self):
        with self.database as conn:
            cur = conn.execute("SELECT uuid FROM requirements ORDER BY seq_no ASC")
            uuids = [row["uuid"] for row in cur.fetchall()]
            for i, uid in enumerate(uuids, start=1):
                conn.execute("UPDATE requirements SET seq_no = ? WHERE uuid = ?", (i, uid))
            conn.commit()


    def update_requirement(self, seq_no: int, field: str, value: str):
        VALID_FIELDS = {"description", "type", "domain"}

        with self.database as conn:
            cur = conn.execute("SELECT * FROM requirements WHERE seq_no = ?", (seq_no,))
            row = cur.fetchone()
            if not row:
                console.print("[bold red]Requirement REQ-{seq_no:03} not found.[/bold red]")
                raise typer.Exit()

            if field and value:
                if field not in VALID_FIELDS:
                    typer.echo(f"Invalid field: {field}. Must be one of: {', '.join(VALID_FIELDS)}.")
                    raise typer.Exit()
                conn.execute(f"UPDATE requirements SET {field} = ? WHERE seq_no = ?", (value, seq_no))
                conn.commit()
                console.print(f"[bold green]Updated REQ-{seq_no:03}: set {field} to '{value}'[/bold green]")
                return

            console.print(f"[bold yellow]Updating REQ-{seq_no:03} interactively. Leave blank to keep existing values.[/bold yellow]")

            for f in VALID_FIELDS:
                current = row[f]
                new_val = typer.prompt(f"{f.capitalize()} [{current}]", default=current)
                conn.execute(f"UPDATE requirements SET {f} = ? WHERE seq_no = ?", (new_val, seq_no))

            conn.commit()
            console.print(f"[bold green]REQ-{seq_no:03} updated successfully![/bold green]")

    def show_requirements(self, req_type: Optional[str] = None, domain: Optional[str] = None, json: Optional[bool] = False):
        with self.database as conn:
            query = "SELECT * FROM requirements WHERE 1=1"
            filters = []
            args = []

            if req_type:
                filters.append("type = ?")
                args.append(req_type)

            if domain:
                filters.append("domain = ?")
                args.append(domain)

            if filters:
                query += " AND " + " ".join(filters)

            cur = conn.execute(query, args)
            rows = cur.fetchall()

            if not json:
                req_table = [["REQ-ID", "Description", "Type", "Domain"]]
                for row in rows:
                    req_table.append([
                        f"REQ-{row['seq_no']:03}",
                        row["description"],
                        row["type"],
                        row["domain"]
                    ])
                if not req_table:
                    console.print("[bold yellow]No requirements found.[/bold yellow]")
                    return

                ReportWriter.print_table_console(req_table, title=None, with_title= False)
            else:
                req_list = []
                for row in rows:
                    req_list.append({
                        "id": f"REQ-{row['seq_no']:03}",
                        "uuid": row["uuid"],
                        "description": row["description"],
                        "type": row["type"],
                        "domain": row["domain"],
                        "linked_tests": row["linked_tests"].split(",") if row["linked_tests"] else [],
                    })

                ReportWriter.print_table_json(req_list)


    def show_characteristic(self, char: str):
        """Show all requirements with a specific characteristic."""

        if char not in ["type", "domain"]:
            console.print(f"[bold red]Invalid characteristic: {char}[/bold red]")
            return

        table = [[char.capitalize()]]
        with self.database:
            values = self.get_characteristic(char)
            for value in values:
                table.append([value])

            ReportWriter.print_table_console(table, title=None, with_title = False)

    def get_characteristic(self, char: str) -> List[str]:
        """Get all unique values for a specific characteristic."""
        if char not in ["type", "domain"]:
            console.print(f"[bold red]Invalid characteristic: {char}[/bold red]")
            return []

        with self.database as conn:
            cur = conn.execute(f"SELECT DISTINCT {char} FROM requirements")
            values = [row[char] for row in cur.fetchall()]
        return sorted(values)

    def get_stats_by_characteristic(self, char: str, value: str, report = None
                                    ) -> Dict[str, int]:
        """Get the number of requirements for each value of a characteristic."""
        if char not in ["type", "domain"]:
            console.print(f"[bold red]Invalid characteristic: {char}[/bold red]")
            return {}

        with self.database as conn:
            cur = conn.execute(f"SELECT COUNT(*) FROM requirements WHERE {char} = ?", (value,))
            total = cur.fetchone()[0]

            cur = conn.execute(
                f"SELECT uuid FROM requirements WHERE {char} = ? AND linked_tests != ''",
                (value,)
            )

            fetched_data = cur.fetchall()
            total_tested = len(fetched_data)

            total_passed = [ report[row["uuid"]]["STATUS"] for row in fetched_data if row["uuid"] in report ] \
                .count("PASSED") if report else 0

        return {"total": total, "tested": total_tested, "passed": total_passed}

    def get_requirements(self) -> Dict[str, Dict[str, str]]:
        """Get all requirements as a list of dictionaries."""
        with self.database as conn:
            cur = conn.execute("SELECT * FROM requirements ORDER BY seq_no ASC")
            reqs = defaultdict(dict)
            for row in cur.fetchall():
                reqs[f"REQ-{row['seq_no']:03}"] = {
                    "uuid": row["uuid"],
                    "description": row["description"],
                    "type": row["type"],
                    "domain": row["domain"],
                    "linked_tests": row["linked_tests"].split(",") if row["linked_tests"] else [],
                }
        return reqs

    def get_requirements_uuids(self) -> Dict[str, str]:
        """Get all requirements as a mapping of REQ-ID to UUID."""
        with self.database as conn:
            cur = conn.execute("SELECT uuid, seq_no FROM requirements")
            req_dict = {f"REQ-{row['seq_no']:03}": row["uuid"] for row in cur.fetchall()}

        return req_dict

    def link_tests(self, tests: list = None, uuid: str = None):
        """Link tests to a requirement by UUID."""

        # tests can be deleted or empty, so we only check if uuid is provided
        if not uuid:
            console.print("[bold red]No UUID provided for linking.[/bold red]")
            return

        if not isinstance(tests, list):
            console.print("[bold red]Tests must be provided as a list.[/bold red]")
            return

        with self.database as conn:
            conn.execute(
                "UPDATE requirements SET linked_tests = ? WHERE uuid = ?",
                (",".join(tests), uuid),
            )


    def create_from_yaml(self, reqs: List[Dict[str, str]]):
        """Create requirements from a YAML-like structure."""
        if not reqs:
            console.print("[bold red]No requirements provided for creation.[/bold red]")
            return

        with self.database as conn:
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


