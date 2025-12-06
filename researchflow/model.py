from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Block(Protocol):
    """
    Marker protocol for all block types.
    Used so that any block can be treated as a `Block`.
    """

    pass


@dataclass
class MarkdownBlock:
    """
    Plain markdown content between semantic blocks.
    """

    content: str


@dataclass
class SummaryBlock:
    """
    Highlighted summary block.
    """

    content: str


@dataclass
class FigureBlock:
    """
    Represents a figure with path and optional caption/alt text.
    """

    path: str
    caption: str | None = None
    alt: str | None = None


@dataclass
class LogBlock:
    """
    Represents raw log / console output.
    """

    content: str


@dataclass
class CodeBlock:
    """
    Represents a code snippet with an optional language and caption.
    """

    language: str | None
    code: str
    caption: str | None = None


@dataclass
class RFlowDocument:
    """
    Fully parsed ResearchFlow document:
    - metadata: raw YAML metadata
    - blocks: ordered list of content blocks
    - path: original file path
    """

    metadata: dict[str, object]
    blocks: list[Block]
    path: Path
