from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .loader import load_rflow_file
from .parser import parse_rflow
from .model import RFlowDocument
from .render import render_document


@dataclass
class SiteDocument:
    """
    Represents a document that will be part of the built site.

    Attributes:
        kind: Logical type of document, e.g. "note" or "experiment".
        slug: URL-friendly identifier used in the output path.
        source_path: Path to the original `.rflow` file.
        document: Parsed RFlowDocument model.
    """

    kind: str
    slug: str
    source_path: Path
    document: RFlowDocument


def discover_documents(workspace_root: Path) -> list[SiteDocument]:
    """
    Scan the workspace for `.rflow` files in `notes/` and `experiments/`,
    load and parse them into SiteDocument objects.

    Rules (matching the v0.1 workspace layout spec):
        - `notes/` contains note documents.
        - `experiments/` contains experiment documents.

    The `type` field in metadata is used when available, otherwise
    it falls back to the directory kind.
    """
    documents: list[SiteDocument] = []

    for kind, subdir in (("note", "notes"), ("experiment", "experiments")):
        dir_path = workspace_root / subdir
        if not dir_path.is_dir():
            continue

        for path in sorted(dir_path.glob("*.rflow")):
            raw = load_rflow_file(path)
            doc = parse_rflow(raw)

            # Determine final kind: prefer metadata if valid
            meta_type = str(doc.metadata.get("type") or kind).lower()
            if meta_type not in ("note", "experiment"):
                meta_type = kind

            # Determine slug: metadata.slug > file name
            slug_value = doc.metadata.get("slug")
            slug = str(slug_value) if slug_value else path.stem

            documents.append(
                SiteDocument(
                    kind=meta_type,
                    slug=slug,
                    source_path=path,
                    document=doc,
                )
            )

    return documents


def build_site(workspace_root: Path, build_root: Path) -> None:
    """
    Build the static site into `build_root` from the given workspace.

    For MVP v0.1 this function:
        - clears the existing build directory
        - discovers all `.rflow` documents
        - renders each document into:
            build/notes/<slug>/index.html
            build/experiments/<slug>/index.html
        - copies `assets/` to `build/assets/` if it exists
    """
    # 1. Reset build directory
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True, exist_ok=True)

    # 2. Discover documents
    documents = discover_documents(workspace_root)

    # 3. Render each document to its respective output path
    for site_doc in documents:
        if site_doc.kind == "note":
            section = "notes"
        else:
            section = "experiments"

        output_dir = build_root / section / site_doc.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        html = render_document(site_doc.document)
        output_path = output_dir / "index.html"
        output_path.write_text(html, encoding="utf-8")

    # 4. Copy assets directory if present
    assets_src = workspace_root / "assets"
    if assets_src.is_dir():
        assets_dst = build_root / "assets"
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
