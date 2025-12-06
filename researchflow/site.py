from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from collections import defaultdict
from typing import Any

from .loader import load_rflow_file
from .parser import parse_rflow
from .model import RFlowDocument
from .render import render_document, get_template_environment


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

    # 5. Build index pages
    build_indexes(documents, build_root)


def _document_to_index_item(site_doc: SiteDocument) -> dict[str, Any]:
    """
    Convert a SiteDocument into a simple dictionary suitable
    for index templates.

    Fields:
        - title
        - kind
        - slug
        - url
        - date
        - summary
        - tags
    """
    meta = site_doc.document.metadata

    title = str(meta.get("title") or site_doc.slug)
    date = meta.get("date")
    summary = meta.get("summary")
    tags = meta.get("tags") or []

    # Ensure tags is a list of strings
    if isinstance(tags, str):
        tags = [tags]
    elif isinstance(tags, list):
        tags = [str(t) for t in tags]
    else:
        tags = []

    section = "notes" if site_doc.kind == "note" else "experiments"
    url = f"/{section}/{site_doc.slug}/"

    return {
        "title": title,
        "kind": site_doc.kind,
        "slug": site_doc.slug,
        "url": url,
        "date": date,
        "summary": summary,
        "tags": tags,
    }


def build_indexes(documents: list[SiteDocument], build_root: Path) -> None:
    """
    Build index pages for the site:

        - Home: build/index.html
        - Notes index: build/notes/index.html
        - Experiments index: build/experiments/index.html
        - Tag pages: build/tags/<tag>/index.html
    """
    env = get_template_environment()

    # Prepare items
    note_items = [
        _document_to_index_item(doc) for doc in documents if doc.kind == "note"
    ]
    experiment_items = [
        _document_to_index_item(doc) for doc in documents if doc.kind == "experiment"
    ]

    # Sort by date descending (string sort works for YYYY-MM-DD)
    def sort_key(item: dict[str, Any]) -> str:
        date = item.get("date")
        return str(date) if date is not None else ""

    note_items.sort(key=sort_key, reverse=True)
    experiment_items.sort(key=sort_key, reverse=True)

    # Build tag map
    tag_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in note_items + experiment_items:
        for tag in item["tags"]:
            tag_map[tag].append(item)

    # Home page
    home_template = env.get_template("home.html")
    home_html = home_template.render(
        site_title="ResearchFlow",
        notes_count=len(note_items),
        experiments_count=len(experiment_items),
        recent_notes=note_items[:5],
        recent_experiments=experiment_items[:5],
        tags=sorted(tag_map.keys()),
    )
    (build_root / "index.html").write_text(home_html, encoding="utf-8")

    # Notes index
    notes_index_template = env.get_template("notes_index.html")
    notes_index_html = notes_index_template.render(items=note_items)
    notes_index_path = build_root / "notes" / "index.html"
    notes_index_path.parent.mkdir(parents=True, exist_ok=True)
    notes_index_path.write_text(notes_index_html, encoding="utf-8")

    # Experiments index
    experiments_index_template = env.get_template("experiments_index.html")
    experiments_index_html = experiments_index_template.render(items=experiment_items)
    experiments_index_path = build_root / "experiments" / "index.html"
    experiments_index_path.parent.mkdir(parents=True, exist_ok=True)
    experiments_index_path.write_text(
        experiments_index_html,
        encoding="utf-8",
    )

    # Tag pages
    tag_template = env.get_template("tag_index.html")
    tags_root = build_root / "tags"
    for tag, items in tag_map.items():
        tag_dir = tags_root / tag
        tag_dir.mkdir(parents=True, exist_ok=True)

        tag_html = tag_template.render(tag=tag, items=items)
        (tag_dir / "index.html").write_text(tag_html, encoding="utf-8")
