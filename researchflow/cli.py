from __future__ import annotations

from pathlib import Path

import typer

from .site import build_site
from .scaffold import create_experiment, create_note

app = typer.Typer(
    help="ResearchFlow - Python-first research publishing engine (MVP v0.1).",
)

new_app = typer.Typer(help="Create new .rflow documents.")
app.add_typer(new_app, name="new")


@app.command("build")
def build(
    workspace: Path = typer.Argument(
        Path("."),
        help="Path to the ResearchFlow workspace (default: current directory).",
    ),
    build_dir: Path = typer.Option(
        None,
        "--build-dir",
        "-b",
        help="Output directory for the built site (default: <workspace>/build).",
    ),
) -> None:
    """
    Build the static site from `.rflow` documents.

    This command scans `notes/` and `experiments/` inside the workspace,
    renders all documents, and writes HTML into the build directory.
    """
    workspace = workspace.resolve()
    final_build_dir = (build_dir or (workspace / "build")).resolve()

    typer.echo(f"Workspace: {workspace}")
    typer.echo(f"Build directory: {final_build_dir}")

    build_site(workspace, final_build_dir)

    typer.echo("✅ Build completed.")


@new_app.command("note")
def new_note(
    title: str = typer.Argument(
        ...,
        help="Title of the new note.",
    ),
    workspace: Path = typer.Option(
        Path("."),
        "--workspace",
        "-w",
        help="Path to the workspace (default: current directory).",
    ),
) -> None:
    """
    Create a new note `.rflow` file under `notes/` with a minimal template.
    """
    workspace = workspace.resolve()
    path = create_note(workspace, title)
    typer.echo(f"✅ Created note: {path}")


@new_app.command("exp")
def new_experiment(
    title: str = typer.Argument(
        ...,
        help="Title of the new experiment.",
    ),
    workspace: Path = typer.Option(
        Path("."),
        "--workspace",
        "-w",
        help="Path to the workspace (default: current directory).",
    ),
) -> None:
    """
    Create a new experiment `.rflow` file under `experiments/`
    with a scaffold tailored for experiments.
    """
    workspace = workspace.resolve()
    path = create_experiment(workspace, title)
    typer.echo(f"✅ Created experiment: {path}")


if __name__ == "__main__":
    app()
