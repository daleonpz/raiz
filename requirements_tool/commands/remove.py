# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
from requirements_tool.utils.database import RequirementsDB

from rich.traceback import install
install(show_locals=True)

def remove(req_id: int):
    """Remove a requirement by ID and renumber the rest."""

    if req_id < 1:
        typer.echo("Requirement ID must be greater than 0.")
        raise typer.Exit(code=1)

    db = RequirementsDB()
    db.rm(req_id)

