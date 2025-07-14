import typer
import yaml
from pathlib import Path
from typing import Optional
import os
import re

app = typer.Typer()

REQS_DIR = Path("requirements")
REQ_FILE = REQS_DIR / "requirements.yaml"


def load_requirements():
    if not REQ_FILE.exists():
        return []
    with open(REQ_FILE) as f:
        return yaml.safe_load(f) or []


def save_requirements(reqs):
    with open(REQ_FILE, "w") as f:
        yaml.dump(reqs, f)


def renumber_requirements(reqs):
    for idx, req in enumerate(reqs, 1):
        req["id"] = f"REQ-{idx:03}"
    return reqs


@app.command()
def add():
    """Add a new requirement."""
    typer.echo("Adding new requirement (like Commitizen)")
    description = typer.prompt("Description")
    req_type = typer.prompt("Type [functional, non-functional, constraint]")
    domain = typer.prompt("Domain [e.g., logging, ble, data-processing]")

    reqs = load_requirements()
    reqs.append({
        "id": f"REQ-{len(reqs)+1:03}",
        "description": description,
        "type": req_type,
        "domain": domain,
        "linked_tests": []
    })
    save_requirements(reqs)
    typer.echo("Requirement added.")


@app.command()
def rm(req_id: str):
    """Remove a requirement and renumber all."""
    reqs = load_requirements()
    reqs = [r for r in reqs if r["id"] != req_id]
    reqs = renumber_requirements(reqs)
    save_requirements(reqs)
    typer.echo(f"Removed {req_id} and renumbered all requirements.")


@app.command()
def list(filter: Optional[str] = typer.Argument(None)):
    """List requirements, optionally filtered by type or domain."""
    reqs = load_requirements()
    if filter:
        key, val = filter.split("=")
        reqs = [r for r in reqs if r.get(key) == val]
    for r in reqs:
        typer.echo(f"{r['id']}: {r['description']} [{r['type']}, {r['domain']}]")


@app.command()
def trace(filter: Optional[str] = typer.Argument(None)):
    """Trace requirements to their test cases."""
    reqs = load_requirements()
    if filter == "with-test":
        reqs = [r for r in reqs if r["linked_tests"]]
    elif filter == "no-test":
        reqs = [r for r in reqs if not r["linked_tests"]]

    for r in reqs:
        tests = ", ".join(r["linked_tests"]) if r["linked_tests"] else "❌ No tests"
        typer.echo(f"{r['id']}: {r['description']} -> {tests}")


@app.command()
def link():
    """Link test cases to requirements by parsing test IDs in test source."""
    reqs = load_requirements()
    test_dir = Path("tests")
    test_map = {r["id"]: [] for r in reqs}

    for test_file in test_dir.rglob("test_*.py"):
        with open(test_file) as f:
            for line in f:
                m = re.search(r"@pytest\.mark\.req\(['\"](REQ-\d{3})['\"]\)", line)
                if m:
                    req_id = m.group(1)
                    if req_id in test_map:
                        test_map[req_id].append(test_file.name)

    for r in reqs:
        r["linked_tests"] = test_map.get(r["id"], [])

    save_requirements(reqs)
    typer.echo("Linked tests to requirements.")


if __name__ == "__main__":
    app()

