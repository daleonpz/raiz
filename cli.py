# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import typer
from requirements_tool.commands import trace, add, remove, show, update
from rich.traceback import install
install(show_locals=True)

app = typer.Typer(help="Software Requirement Traceability CLI")

# Add subcommands
# app.command("trace")(trace.trace)
app.command("add")(add.add)
app.command("remove")(remove.remove)
# app.command("show")(show.show)
app.command("update")(update.update)

if __name__ == "__main__":
    app()

