from __future__ import annotations

from pathlib import Path

import typer

from .site import build_site

app = typer.Typer(
    help="ResearchFlow - Python-first research publishing engine (MVP v0.1).",
)


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


if __name__ == "__main__":
    app()
