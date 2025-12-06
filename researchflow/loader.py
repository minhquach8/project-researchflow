from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class RFlowRawDocument:
    """
    Represents a raw `.rflow` document split into:
        - metadata: parsed YAML dictionary
        - body: markdown text
        - path: original file location
    """

    metadata: dict[str, object]
    body: str
    path: Path


def load_rflow_file(path: Path) -> RFlowRawDocument:
    """
    Load a `.rflow` file from disk and split it into metadata + body.

    Rules from `.rflow v1` spec:
        - File must start with a line containing exactly '---'
        - Metadata ends at the next line of '---'
        - Body starts after a blank line following metadata
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Invalid .rflow file (missing opening ---): {path}")

    # Find closing '---'
    try:
        end_index = lines.index("---", 1)
    except ValueError:
        raise ValueError(f"Invalid .rflow file (missing close ---): {path}")

    yaml_block = "\n".join(lines[1:end_index])
    body_block = "\n".join(lines[end_index + 1 :]).lstrip("\n")

    metadata = yaml.safe_load(yaml_block) or {}

    return RFlowRawDocument(
        metadata=metadata,
        body=body_block,
        path=path,
    )
