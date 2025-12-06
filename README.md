# ResearchFlow (MVP v0.1)

**A modern, Python-first research publishing engine.**
Write `.rflow` documents → build a clean research website → serve locally → publish anywhere.

ResearchFlow is designed for researchers, engineers, students, and labs who want:

- lightweight, readable research notes,
- reproducible experiment logs,
- clean static research websites,
- zero configuration,
- full control over source files.

MVP v0.1 focuses on **core functionality only**:
**write → build → serve**, with a minimal, modern theme inspired by GitBook.

---

## 🚀 Features (v0.1)

### Core capabilities

- **`.rflow` document format**
  - YAML metadata
  - Markdown body
  - semantic blocks:
    - `summary`
    - `figure`
    - `log`
    - `code`

- **Static site generator**
  - automatic pages for:
    - notes
    - experiments
    - tags
    - home (recent notes/experiments + tag cloud)

  - syntax highlighting ready (CSS-based)
  - mobile-friendly, modern typography (dark theme)

- **Command-line interface (CLI)**

  ```
  rflow new note "Title"
  rflow new exp  "Title"
  rflow build
  rflow serve
  ```

### Non-goals for MVP v0.1

(Not included yet — planned for future versions.)

- AI integration
- code execution
- Jupyter/Notebook import
- experiment tracking
- cloud sync
- WYSIWYG editor
- light/dark theme switching

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/project-researchflow.git
cd project-researchflow
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

You're ready to use ResearchFlow.

---

## 📝 The `.rflow` Document Format

A `.rflow` file contains:

1. **YAML metadata**

```yaml
---
title: My Note
type: note # or: experiment
tags: [ai, speech]
date: 2025-12-06
summary: "Short description"
slug: my-note
---
```

2. **Markdown body**

```markdown
# Heading

Normal markdown text, lists, code, etc.
```

3. **Semantic blocks**

```
:::summary
This is a short summary block.
:::

:::figure
path: assets/image.png
caption: Example figure.
:::

:::log
epoch=1  acc=0.72
epoch=2  acc=0.81
:::

:::code
lang: python
caption: Training loop.

def train(...):
    ...
:::
```

These blocks allow clearer structure for research notes and experiment reports.

---

## 📂 Project Workspace Layout (MVP v0.1)

Every ResearchFlow workspace follows this structure:

```
project/
  notes/
      my-note.rflow
  experiments/
      exp001.rflow
  assets/
  templates/         # default theme included in the repo
  build/             # generated output (created automatically)
  rflow.yml          # optional future config
```

The generator will:

- scan `notes/` and `experiments/`
- build everything into `build/`
- preserve relative paths to `assets/`

---

## 🎯 CLI Usage

### Create a new note

```bash
python -m researchflow.cli new note "My First Note"
```

Creates:

```
notes/my-first-note.rflow
```

### Create a new experiment

```bash
python -m researchflow.cli new exp "Experiment 001 – Baseline"
```

Creates:

```
experiments/experiment-001-baseline.rflow
```

### Build the site

```bash
python -m researchflow.cli build
```

Creates the full static website in:

```
build/
```

### Serve the site locally

```bash
python -m researchflow.cli serve
```

Open in your browser:

```
http://127.0.0.1:8000/
```

Serve without rebuilding:

```bash
python -m researchflow.cli serve --no-build
```

Change port:

```bash
python -m researchflow.cli serve --port 9000
```

---

## 🌐 Generated Website Structure

```
build/
  index.html               # Home page
  notes/
    index.html             # Notes index
    <slug>/
       index.html          # Individual note
  experiments/
    index.html             # Experiments index
    <slug>/
       index.html          # Individual experiment
  tags/
    <tag>/
       index.html          # Tag page
  assets/
    ...                    # Copied from workspace
```

This structure is **compatible with GitHub Pages, Netlify, Cloudflare Pages**, or any static hosting platform.

---

## 🧪 Example Document

Here is a minimal example note:

```markdown
---
title: Hello ResearchFlow
type: note
tags: [intro]
date: 2025-12-06
slug: hello
summary: "Quick introduction to ResearchFlow."
---

# Hello ResearchFlow

This is a demo note.

:::summary
ResearchFlow MVP v0.1 enables writing, building, and serving
research websites with a clean modern theme.
:::

## Figure Example

:::figure
path: assets/confusion-matrix.png
caption: Demo confusion matrix.
:::

## Log Example

:::log
epoch=1 loss=0.42 acc=0.75
epoch=2 loss=0.38 acc=0.80
:::

## Code Example

:::code
lang: python
caption: Example training loop.

def train(model, data_loader):
for batch in data_loader:
model.step(batch)
:::
```

---

## 🛠 Architecture Overview

```
.rflow file
   ↓
Loader (YAML + body)
   ↓
Parser (Markdown + semantic blocks)
   ↓
RFlowDocument model
   ↓
Renderer (Jinja2 templates)
   ↓
Static site generator
   ↓
build/
```

Layers are cleanly separated:

- modify theme → edit `templates/`
- change syntax → modify parser
- extend CLI → edit `researchflow/cli.py`

---

## ⚠️ Limitations (MVP v0.1)

- No AI-assisted authoring.
- No notebook importing.
- No code execution.
- No experiment tracking.
- No light/dark theme switch.
- No plugin system.
- Some features (e.g., slugify, tag normalisation) are minimal.

Everything above is intentionally deferred to keep MVP simple and reliable.

---

## 🚧 Roadmap (Post v0.1)

### v0.2

- Light/dark theme switch
- Improved Markdown renderer (TOC, footnotes)
- Better Unicode slugify

### v0.3

- Notebook import (`.ipynb` → `.rflow`)
- Built-in charts (matplotlib/plotly integrations)

### v0.4

- Experiment tracking (metrics table, runs overview)
- Asset versioning

### v0.5+

- AI-assisted writing
- Live editor
- Plugin system
- Multi-theme architecture

---

## 📜 License

MIT License.

---

## 💬 Contributing

Pull requests, issues, and feature suggestions are welcome.

If you build your own research notebook/blog using ResearchFlow, please share—your examples help shape the roadmap.

---

## ⭐ Acknowledgements

ResearchFlow is inspired by:

- Markdown (John Gruber)
- Jinja2 (Armin Ronacher)
- GitBook / Notion / Quarto
- The scientific computing community
