# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
from requirements_tool.utils.database import RequirementsDB

from rich.traceback import install
install(show_locals=True)

def add():
    """Add a new requirement interactively."""
    description = typer.prompt("Description")
    req_type = typer.prompt("Type [functional, non-functional, constraint]")
    domain = typer.prompt("Domain [e.g., logging, ble, data-processing]")

    db = RequirementsDB()
    db.add_requirement(description=description, req_type=req_type, domain=domain)

