# ResearchFlow `.rflow` Format – Version 1 (MVP)

This document defines the **version 1** of the `.rflow` file format used by ResearchFlow MVP v0.1.

A `.rflow` file is a text file with three key ideas:

1. **YAML front matter** for metadata.
2. **Markdown body** for main content.
3. **Marker-based blocks** for semantic content (summary, figure, log, code).

The goal is to keep the format:

- easy to write by hand,
- easy to parse in Python,
- stable enough to build a static research website.

---

## 1. File placement and extension

- File extension: **`.rflow`**
- Typical locations inside a ResearchFlow workspace:

```text
  project/
    notes/
      my-note.rflow
    experiments/
      exp001.rflow
    assets/
    ...
```

- In MVP v0.1, ResearchFlow assumes:
  - `notes/` contains files with `type: note`.
  - `experiments/` contains files with `type: experiment`.

Future versions may relax or extend these rules, but v0.1 keeps them strict.

---

## 2. Overall file structure

Each `.rflow` file has exactly two main parts:

1. **YAML front matter** (metadata), delimited by `---` at the beginning and `---` on its own line.
2. **Markdown body**, starting after a blank line following the closing `---`.

Example:

```text
---
title: My First Note
type: note
tags: [ai, speech]
date: 2025-12-06
summary: Short one-line summary for index pages.
---

# This is a note

Regular Markdown content here…

:::summary
This is an optional extended summary block.
It can span multiple lines.
:::
```

Rules:

- The file **must start** with `---` in the first line.
- YAML front matter ends at the next line containing only `---`.
- There should be **at least one blank line** between the closing `---` and the Markdown body.
- Line endings: `\n` (Unix-style) are recommended.

---

## 3. YAML metadata (front matter)

The front matter is parsed as YAML.

### 3.1 Required fields

| Field | Type   | Description                                        |
| ----- | ------ | -------------------------------------------------- |
| title | string | Human-readable title of the note or experiment.    |
| type  | string | Either `"note"` or `"experiment"`.                 |
| date  | string | Date in `YYYY-MM-DD` format (ISO-like, date only). |

### 3.2 Optional fields

| Field   | Type        | Description                                                             |
| ------- | ----------- | ----------------------------------------------------------------------- |
| tags    | list of str | Simple tags for grouping and navigation (e.g. `[ai, speech, ml]`).      |
| summary | string      | Short text used for index cards; usually one or two sentences.          |
| slug    | string      | Optional explicit slug. If missing, slug is derived from the file name. |

Notes:

- `type` controls how the item appears in navigation (`notes` vs `experiments`).
- `slug` is optional in v0.1; by default, the slug comes from the file name without extension.
- Tags should be simple identifiers (no commas); spaces are allowed but hyphens are recommended.

Example front matter:

```yaml
---
title: Exploring Speech Features for Dementia
type: experiment
tags: [ai, speech, dementia]
date: 2025-11-30
summary: First experiment exploring MFCC-based features for early dementia detection.
slug: exp-speech-dementia-mfcc-v1
---
```

---

## 4. Markdown body

After the front matter, the rest of the file is the **Markdown body**.

Everything that is valid basic Markdown is allowed:

- headings (`#`, `##`, …),
- paragraphs,
- bullet and numbered lists,
- inline code, bold, italics,
- fenced code blocks (`python ` etc.).

On top of that, `.rflow` adds **marker-based blocks**.

---

## 5. Marker-based blocks (v1)

Marker-based blocks use a simple pattern:

```text
:::blockname
...content...
:::
```

General rules:

- The opening marker starts with `:::` immediately followed by the block name, with no extra characters on the line.
- The closing marker is exactly `:::` on a line by itself.
- There must be **no nested blocks** in v1 (i.e. a block may not contain another `:::` block).
- Indentation is not significant for the markers; they should start at the first column.

Supported blocks in v1:

1. `summary`
2. `figure`
3. `log`
4. `code`

Any unknown block name should be handled gracefully (e.g. ignored or rendered as generic box) but v0.1 only needs the four blocks above.

---

## 6. `summary` block

Purpose: highlight a short summary or key takeaway.

Syntax:

```text
:::summary
This is a highlighted summary.

It may contain multiple paragraphs of Markdown.
:::
```

Rules:

- Content is parsed as Markdown.
- Typically used near the top of the note or experiment.
- In the HTML theme, it will be rendered as a visually distinct box.

---

## 7. `figure` block

Purpose: represent an image with metadata (path, caption, alt text).

Syntax:

```text
:::figure
path: assets/img1.png
caption: Confusion matrix for model v1.
alt: Confusion matrix heatmap.
:::
```

Fields inside the block:

- `path` (required): string, path to the image file, relative to the project root (e.g. `assets/…`).
- `caption` (optional): string, caption shown under the figure.
- `alt` (optional): string, alt text for accessibility.

Notes:

- v0.1 assumes images are copied or accessible under `build/assets/…`.
- If `alt` is missing, the renderer may fall back to the `caption` or an empty string.

---

## 8. `log` block

Purpose: show raw text output such as training logs, console output, metrics history.

Syntax:

```text
:::log
epoch 1 - loss=0.523
epoch 2 - loss=0.412
epoch 3 - loss=0.398
:::
```

Rules:

- Content is treated as preformatted text (no Markdown parsing required inside).
- Line breaks should be preserved.
- The HTML theme should render this in a monospaced box, similar to a terminal.

---

## 9. `code` block

Purpose: attach code with an explicit language and optional caption, without relying on Markdown fenced blocks.

Syntax:

```text
:::code
lang: python
caption: Simple training loop.

def train():
    for epoch in range(10):
        print(f"Epoch {epoch}")
:::
```

Fields and content:

- First non-empty lines may contain simple `key: value` pairs:
  - `lang` (optional but recommended): language identifier, e.g. `python`, `bash`, `yaml`.
  - `caption` (optional): short description for the code snippet.

- After one blank line, remaining lines are treated as raw code.

Example with no caption:

```text
:::code
lang: bash

python train.py --epochs 50 --lr 1e-3
:::
```

Notes:

- v0.1 does not require a strict YAML parser for the mini header inside the block.
- A simple `key: value` parser line by line is sufficient.

---

## 10. Unknown or unsupported blocks

In v1, only the four blocks above are considered “official”. For robustness:

- The parser should recognise any pattern `:::something … :::`.
- Unknown block names should not crash the parser.
- A simple strategy for v0.1:
  - Treat unknown blocks as generic containers, or
  - Ignore them when generating HTML.

---

## 11. Constraints and limitations in v1

To keep the format simple and the parser robust:

- No nested marker blocks.
- `:::blockname` and closing `:::` must both start at column 0.
- YAML front matter must be valid YAML; otherwise, the file is considered invalid.
- Date is always stored as `YYYY-MM-DD` string (no time-of-day in v1).

Future versions may add:

- richer block types,
- nested blocks,
- time-aware metadata,
- cross-references.

For MVP v0.1, this specification is considered **frozen**.
