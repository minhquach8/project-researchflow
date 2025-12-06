from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


def slugify(value: str) -> str:
    """
    Create a simple, URL-friendly slug from a title.

    Rules (v0.1, deliberately simple):
        - lower-case
        - replace whitespace with '-'
        - remove characters that are not alphanumeric or '-'
        - collapse multiple '-' into one
        - strip leading/trailing '-'
    """
    value = value.strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\-]", "", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "untitled"


def _ensure_unique_path(base_dir: Path, slug: str) -> Path:
    """
    Ensure the `.rflow` file path is unique inside base_dir.

    If `slug.rflow` exists, try `slug-2.rflow`, `slug-3.rflow`, ...
    """
    candidate = base_dir / f"{slug}.rflow"
    counter = 2
    while candidate.exists():
        candidate = base_dir / f"{slug}-{counter}.rflow"
        counter += 1
    return candidate


def create_note(workspace_root: Path, title: str) -> Path:
    """
    Create a new note `.rflow` file under `notes/` with a minimal template.

    Returns the path to the created file.
    """
    today = date.today().isoformat()
    slug = slugify(title)

    notes_dir = workspace_root / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    path = _ensure_unique_path(notes_dir, slug)

    content = f"""---
title: {title}
type: note
tags: []
date: {today}
summary: ""
slug: {slug}
---

# {title}

Write your note here.
"""

    path.write_text(content, encoding="utf-8")
    return path


def create_experiment(workspace_root: Path, title: str) -> Path:
    """
    Create a new experiment `.rflow` file under `experiments/`
    with a slightly richer scaffold.

    Returns the path to the created file.
    """
    today = date.today().isoformat()
    slug = slugify(title)

    experiments_dir = workspace_root / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    path = _ensure_unique_path(experiments_dir, slug)

    content = f"""---
title: {title}
type: experiment
tags: []
date: {today}
summary: ""
slug: {slug}
---

# {title}

:::summary
Short summary of this experiment.
:::

## Objective

Describe the main question or hypothesis here.

## Setup

- Data:
- Model:
- Metrics:

## Results

Summarise key findings here.

## Notes

Additional observations, caveats, or follow-up ideas.
"""

    path.write_text(content, encoding="utf-8")
    return path
