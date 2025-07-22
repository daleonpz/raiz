# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import sqlite3
from typing import Optional, List, Dict
import uuid
from pathlib import Path
import typer
from rich.traceback import install
install(show_locals=True)

from rich.console import Console

REQ_CACHE_DIR = Path(".req_cache")
REQ_CACHE_DIR.mkdir(exist_ok=True)
DB_PATH = REQ_CACHE_DIR / "requirements.db"

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
                    domain TEXT NOT NULL
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

    def show_requirements(self, req_type: Optional[str] = None, domain: Optional[str] = None):
        with self.database as conn:
            query = "SELECT seq_no, description, type, domain FROM requirements"
            filters = []
            args = []

            if req_type:
                filters.append("type = ?")
                args.append(type)

            if domain:
                filters.append("domain = ?")
                args.append(domain)

            if filters:
                query += " WHERE " + " AND ".join(filters)

            cur = conn.execute(query, args)
            rows = cur.fetchall()

            for row in rows:
                console.print(f"[bold cyan]REQ-{row['seq_no']:03}[/bold cyan]: {row['description']} "
                              f"[dim][{row['type']}, {row['domain']}][/dim]")

    def show_characteristic(self, char: str):
        """Show all requirements with a specific characteristic."""

        if char not in ["type", "domain"]:
            console.print(f"[bold red]Invalid characteristic: {char}[/bold red]")
            return

        with self.database as conn:
            cur = conn.execute(f"SELECT DISTINCT {char} FROM requirements")
            values = sorted(row[char] for row in cur.fetchall())
            console.print(f"[bold green]{char.capitalize()}s:[/bold green]")
            for value in values:
                console.print(f"- {value}")



