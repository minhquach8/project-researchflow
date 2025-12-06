from __future__ import annotations

from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .model import (
    Block,
    CodeBlock,
    FigureBlock,
    LogBlock,
    MarkdownBlock,
    RFlowDocument,
    SummaryBlock,
)


def _create_jinja_environment() -> Environment:
    """
    Create a Jinja2 environment pointing to the project's `templates/` folder.

    For MVP v0.1 we assume the templates directory sits at:
    project_root / "templates"
    """
    # researchflow/render.py → researchflow/ → project root
    project_root = Path(__file__).resolve().parent.parent
    templates_dir = project_root / "templates"

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        enable_async=False,
    )
    return env


_ENV = _create_jinja_environment()


def render_document(doc: RFlowDocument) -> str:
    """
    Render a single RFlowDocument into a full HTML page string.

    This is the main entry point for turning a parsed `.rflow`
    document into HTML for the MVP v0.1.
    """
    template = _ENV.get_template("document.html")
    blocks_html = [_render_block(block) for block in doc.blocks]

    return template.render(
        doc=doc,
        blocks_html=blocks_html,
    )


def _render_block(block: Block) -> str:
    """
    Render an individual block into a small HTML fragment.

    Note:
        - For v0.1, markdown content is not yet converted to rich HTML.
          It is shown as preformatted text so that the structure works.
        - In later steps, we will integrate a markdown renderer and
          syntax highlighting for code.
    """
    if isinstance(block, SummaryBlock):
        content = escape(block.content)
        return (
            "<section class='rf-block-summary'>"
            "<div class='rf-block-summary-title'>Summary</div>"
            f"<div>{content}</div>"
            "</section>"
        )

    if isinstance(block, FigureBlock):
        # We escape caption and alt, but path is assumed to be a safe relative URL.
        alt = escape(block.alt) if block.alt else ""
        caption = escape(block.caption) if block.caption else ""
        src = escape(block.path)
        caption_html = (
            f"<div class='rf-block-figure-caption'>{caption}</div>" if caption else ""
        )
        return (
            "<figure class='rf-block-figure'>"
            f"<img src='{src}' alt='{alt}' />"
            f"{caption_html}"
            "</figure>"
        )

    if isinstance(block, LogBlock):
        content = escape(block.content)
        return f"<pre class='rf-block-log'>{content}</pre>"

    if isinstance(block, CodeBlock):
        code = escape(block.code)
        language_class = f" language-{block.language}" if block.language else ""
        caption_html = (
            f"<div class='rf-block-code-caption'>{escape(block.caption)}</div>"
            if block.caption
            else ""
        )
        return (
            "<section class='rf-block-code'>"
            f"<pre><code class='{language_class}'>{code}</code></pre>"
            f"{caption_html}"
            "</section>"
        )

    if isinstance(block, MarkdownBlock):
        # Temporary behaviour: show raw markdown as-is.
        # A later step will introduce a markdown renderer.
        content = escape(block.content)
        return f"<div class='rf-block-markdown'>{content}</div>"

    # Fallback: unknown block type → escaped repr
    content = escape(repr(block))
    return f"<div class='rf-block-unknown'>{content}</div>"
