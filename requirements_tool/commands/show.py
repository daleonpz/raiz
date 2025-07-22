# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

from typing import Optional
from rich.console import Console

console = Console()

from requirements_tool.utils.database import RequirementsDB

from rich.traceback import install
install(show_locals=True)

def show_requirements(req_type: Optional[str] = None, domain: Optional[str] = None):
    """Show requirements with optional filtering by type/domain."""
    db = RequirementsDB()
    db.show_requirements(req_type, domain)

def show_types():
    """Show all unique types."""
    db = RequirementsDB()
    db.show_characteristic("type")

def show_domains():
    """Show all unique domains."""
    db = RequirementsDB()
    db.show_characteristic("domain")
