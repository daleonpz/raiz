# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
import requirements_tool.commands as commands
from rich.traceback import install
install(show_locals=True)

app = typer.Typer(help="Software Requirement Traceability CLI")
show_app = typer.Typer()
# sync_app = typer.Typer()

app.add_typer(show_app, name="show", help="Show requirements, types, or domains")
# app.add_typer(sync_app, name="sync", help="Sync requirements with YAML file")

# Add subcommands
app.command("trace")(commands.trace)
app.command("add")(commands.add)
app.command("remove")(commands.remove)
app.command("update")(commands.update)

show_app.command("domains")(commands.show_domains)
show_app.command("types")(commands.show_types)
show_app.command("all")(commands.show_requirements)

# sync_app.command("to-yaml")(commands.sync_to_yaml)
# sync_app.command("from-yaml")(commands.sync_from_yaml)

if __name__ == "__main__":
    app()

