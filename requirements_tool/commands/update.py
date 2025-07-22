# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
from rich.console import Console
from requirements_tool.utils.database import RequirementsDB

from rich.traceback import install
install(show_locals=True)

VALID_FIELDS = {"description", "type", "domain"}

console = Console()

def update(req_id: int, field: str = None, value: str = None):
    """Update a requirement by REQ ID. Interactive or field-based."""
    db = RequirementsDB()
    db.update_requirement(req_id, field, value)

