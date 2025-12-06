from __future__ import annotations

from pathlib import Path

from .loader import RFlowRawDocument
from .model import (
    Block,
    CodeBlock,
    FigureBlock,
    LogBlock,
    MarkdownBlock,
    RFlowDocument,
    SummaryBlock,
)


def parse_rflow(raw: RFlowRawDocument) -> RFlowDocument:
    """
    Parse a raw `.rflow` document (metadata + body text) into
    a structured RFlowDocument with semantic blocks.

    Supported block markers (from v1 spec):

    - :::summary
    - :::figure
    - :::log
    - :::code
    """
    lines = raw.body.splitlines()
    index = 0
    blocks: list[Block] = []
    current_plain: list[str] = []

    def flush_plain_block() -> None:
        """Flush accumulated plain markdown into a MarkdownBlock."""
        if current_plain:
            content = "\n".join(current_plain).strip("\n")
            if content:
                blocks.append(MarkdownBlock(content=content))
            current_plain.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        # Not a block start → accumulate as plain markdown
        if not stripped.startswith(":::"):
            current_plain.append(line)
            index += 1
            continue

        # If we reach here, this line starts with ":::"
        # Try to recognise a supported block.
        flush_plain_block()  # End any plain markdown before block

        if stripped == ":::summary":
            block, index = _parse_summary_block(lines, index + 1)
            blocks.append(block)
            continue

        if stripped == ":::figure":
            block, index = _parse_figure_block(lines, index + 1)
            blocks.append(block)
            continue

        if stripped == ":::log":
            block, index = _parse_log_block(lines, index + 1)
            blocks.append(block)
            continue

        if stripped == ":::code":
            block, index = _parse_code_block(lines, index + 1)
            blocks.append(block)
            continue

        # Unknown block type: treat marker line as plain markdown
        current_plain.append(line)
        index += 1

    # Flush any remaining plain markdown at end of document
    flush_plain_block()

    return RFlowDocument(
        metadata=raw.metadata,
        blocks=blocks,
        path=raw.path,
    )


def _consume_until_end_marker(
    lines: list[str], start_index: int
) -> tuple[list[str], int]:
    """
    Consume lines until a closing ':::' marker is found.

    Returns:
        (consumed_lines, next_index)
    where next_index is the position after the closing marker.
    """
    collected: list[str] = []
    index = start_index

    while index < len(lines):
        line = lines[index]
        if line.strip() == ":::":  # closing marker
            return collected, index + 1
        collected.append(line)
        index += 1

    # If we reach here, no closing marker was found.
    # For v0.1 we just return everything; renderer can still do something.
    return collected, index


def _parse_summary_block(
    lines: list[str], start_index: int
) -> tuple[SummaryBlock, int]:
    """
    Parse a `:::summary` block.
    Content is treated as markdown text until closing `:::` line.
    """
    content_lines, next_index = _consume_until_end_marker(lines, start_index)
    content = "\n".join(content_lines).strip("\n")
    return SummaryBlock(content=content), next_index


def _parse_log_block(lines: list[str], start_index: int) -> tuple[LogBlock, int]:
    """
    Parse a `:::log` block.
    Content is treated as raw preformatted text.
    """
    content_lines, next_index = _consume_until_end_marker(lines, start_index)
    content = "\n".join(content_lines).rstrip("\n")
    return LogBlock(content=content), next_index


def _parse_figure_block(lines: list[str], start_index: int) -> tuple[FigureBlock, int]:
    """
    Parse a `:::figure` block containing simple key: value lines.
    Expected keys:
    - path (required)
    - caption (optional)
    - alt (optional)
    """
    content_lines, next_index = _consume_until_end_marker(lines, start_index)

    data: dict[str, str] = {}
    for raw_line in content_lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip()

    path = data.get("path", "")
    caption = data.get("caption")
    alt = data.get("alt")

    return FigureBlock(path=path, caption=caption, alt=alt), next_index


def _parse_code_block(lines: list[str], start_index: int) -> tuple[CodeBlock, int]:
    """
    Parse a `:::code` block.

    Structure:
        - optional mini-header of `key: value` lines (e.g. lang, caption)
        - a blank line
        - raw code content
    """
    content_lines, next_index = _consume_until_end_marker(lines, start_index)

    header: dict[str, str] = {}
    code_lines: list[str] = []

    in_header = True
    for raw_line in content_lines:
        if in_header:
            # Header continues until a blank line
            if not raw_line.strip():
                in_header = False
                continue

            stripped = raw_line.strip()
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                header[key.strip()] = value.strip()
                continue

            # If a non `key: value` line appears, header ends
            in_header = False
            code_lines.append(raw_line)
        else:
            code_lines.append(raw_line)

    language = header.get("lang")
    caption = header.get("caption")
    code = "\n".join(code_lines).rstrip("\n")

    return CodeBlock(language=language, code=code, caption=caption), next_index
