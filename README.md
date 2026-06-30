# MarkForge

Professional PDF generation from JSON content via ReportLab. A deterministic markdown-to-PDF converter with no external dependencies like Chrome, LaTeX, or wkhtmltopdf.

## Features

- **Professional PDF output** using ReportLab's Platypus engine
- **Markdown to JSON conversion** with Pandoc-style YAML frontmatter
- **Cover page** with title, subtitle, author, date, and metadata table
- **Table of Contents** with dotted leaders and page numbers (two-pass rendering)
- **Back-of-book Index** with `<<term>>` markdown syntax
- **Rich text formatting**: bold, italic, links, inline code, subscripts, superscripts
- **Lists**: bullet lists and ordered lists
- **Code blocks**: fenced code blocks with syntax highlighting placeholders
- **Tables**: pipe tables with headers, alternating rows, and proportional column widths
- **Call-out boxes**: highlight boxes with colored left border
- **Images**: embedded images with optional captions
- **Custom fonts**: register TTF fonts for sans, serif, and mono families
- **System font detection**: automatic Menlo registration on macOS for Unicode support
- **Theming**: customizable color schemes (primary, accent, light, text, muted)
- **Page chrome**: configurable headers and footers with placeholders
- **Watermarks**: diagonal semi-transparent watermarks
- **Page configuration**: A4/Letter/Legal sizes, portrait/landscape orientation
- **Section numbering**: automatic hierarchical numbering (1., 1.1, 1.2)

## Installation

```bash
pip install markforge
```

Or from source:

```bash
git clone https://github.com/cesar/markforge.git
cd markforge
pip install -e .
```

## Quick Start

### From Markdown

Create a markdown file with YAML frontmatter:

```markdown
---
title: "My Document"
subtitle: "A professional PDF"
author: "John Doe"
date: "June 2026"
toc: true
index: true
---

## Introduction

This is **bold** and *italic* text. You can also use `inline code`.

## Features

- Bullet list item 1
- Bullet list item 2

1. Ordered item 1
2. Ordered item 2

## Code

```python
def hello():
    print("Hello, World!")
```

## Table

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

Convert to PDF:

```bash
markforge-convert document.md output.pdf
```

### From JSON

Create a JSON content file:

```json
{
  "title": "My Document",
  "subtitle": "A professional PDF",
  "output": "output.pdf",
  "show_toc": true,
  "show_index": true,
  "theme": {
    "primary": "#2E86AB",
    "accent": "#E94560"
  },
  "sections": [
    {
      "heading": "Introduction",
      "body": "This is <b>bold</b> and <i>italic</i> text."
    }
  ]
}
```

Generate PDF:

```bash
markforge content.json
```

## CLI Usage

### markforge-convert

Convert markdown files to PDF:

```bash
markforge-convert input.md [output.pdf]
```

If no output path is specified, it defaults to `{input_stem}.pdf`.

### markforge

Generate PDF from JSON content:

```bash
markforge content.json
```

Or use as a module:

```bash
python -m markforge content.json
```

## Content Schema

The JSON schema accepted by `build_pdf()`:

```json
{
  "title": "string (required)",
  "subtitle": "string",
  "output": "string",
  "page_size": "A4 | Letter | Legal",
  "orientation": "portrait | landscape",
  "show_toc": true,
  "show_index": true,
  "show_cover": true,
  "show_footer_date": true,
  "watermark": "string",
  "fonts": {
    "sans": {
      "regular": "path/to/font.ttf",
      "bold": "path/to/font-bold.ttf",
      "italic": "path/to/font-italic.ttf",
      "bold_italic": "path/to/font-bolditalic.ttf"
    },
    "mono": {
      "regular": "path/to/mono.ttf",
      "bold": "path/to/mono-bold.ttf"
    },
    "serif": {
      "regular": "path/to/serif.ttf",
      "bold": "path/to/serif-bold.ttf",
      "italic": "path/to/serif-italic.ttf",
      "bold_italic": "path/to/serif-bolditalic.ttf"
    }
  },
  "header_footer": {
    "header": {
      "show": true,
      "left": "string",
      "right": "string"
    },
    "footer": {
      "show": true,
      "left": "string",
      "center": "string",
      "right": "string"
    }
  },
  "theme": {
    "primary": "#RRGGBB",
    "accent": "#RRGGBB",
    "light": "#RRGGBB",
    "text": "#RRGGBB",
    "muted": "#RRGGBB"
  },
  "meta": {
    "key": "value"
  },
  "sections": [
    {
      "heading": "string (required)",
      "body": "string (with XML inline tags)",
      "bullets": ["string"],
      "ordered_list": ["string"],
      "highlight": "string",
      "image": {
        "path": "string",
        "width": 1.0,
        "height": 1.0,
        "caption": "string"
      },
      "code": "string",
      "language": "string",
      "table": {
        "headers": ["col1", "col2"],
        "rows": [["cell1", "cell2"]],
        "col_widths": [0.5, 0.5]
      },
      "page_break": true,
      "note": "string"
    }
  ]
}
```

## Markdown Syntax

### Frontmatter

YAML frontmatter with the following keys:

- `title`: Document title (required)
- `subtitle`: Document subtitle
- `author`: Author name
- `date`: Date string
- `toc`: Enable table of contents (`true`/`false`)
- `index`: Enable back-of-book index (`true`/`false`)
- `number_sections`: Enable section numbering (`true`/`false`)
- `titlepage-rule-color`: Hex color for cover page accent bar
- Theme colors: `primary`, `accent`, `light`, `text`, `muted`

### Headings

- `# Level 1` and `## Level 2`: Create new sections
- `### Level 3` through `###### Level 6`: Render as bold in body text

### Inline Formatting

- `**bold**` or `__bold__`: Bold text
- `*italic*` or `_italic_`: Italic text
- `***bold italic***` or `___bold italic___`: Bold and italic
- `` `code` ``: Inline code with gray background
- `[link text](url)`: Hyperlink
- `<<term>>`: Index term for back-of-book index

### Lists

- `- Item`: Bullet list
- `1. Item`: Ordered list

### Code Blocks

Fenced code blocks with optional language:

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Tables

Pipe tables with optional caption:

```markdown
Table: My Table Caption

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Blockquotes

Lines starting with `>` create highlight boxes:

```markdown
> This is a call-out box with a colored left border.
```

## Configuration

### Fonts

Register custom TTF fonts via the `fonts` block. Font names should follow the convention `CustomSans-Bold` to enable bold/italic resolution.

On macOS, Menlo is automatically registered as the monospace font for Unicode support.

### Header/Footer

Configure headers and footers with placeholders:

- `{page}`: Current page number
- `{date}`: Document date
- `{title}`: Document title
- `{version}`: Document version (from meta)

Example:

```json
{
  "header_footer": {
    "header": {
      "show": true,
      "left": "{title}",
      "right": "{date}"
    },
    "footer": {
      "show": true,
      "left": "Confidential",
      "center": "{page}",
      "right": "v{version}"
    }
  }
}
```

### Theming

Customize colors with the `theme` block:

```json
{
  "theme": {
    "primary": "#2E86AB",
    "accent": "#E94560",
    "light": "#F8F9FA",
    "text": "#212529",
    "muted": "#6C757D"
  }
}
```

## Python API

```python
from markforge import build_pdf

content = {
    "title": "My Document",
    "sections": [
        {
            "heading": "Introduction",
            "body": "Hello, World!"
        }
    ]
}

build_pdf(content, "output.pdf")
```

## Testing

Run the test suite:

```bash
python test/runner.py
```

Run individual tests:

```bash
markforge-convert test/basic.md
markforge-convert test/formatting.md
markforge-convert test/tables.md
markforge-convert test/code.md
markforge-convert test/lists.md
markforge-convert test/comprehensive.md
```

## Project Structure

```
markforge/
├── markforge/
│   ├── __init__.py          # Public API re-exports
│   ├── core.py              # build_pdf(), CLI main()
│   ├── schema.py            # Content validation
│   ├── theme.py             # Theme building
│   ├── fonts.py             # Font registration
│   ├── chrome.py            # Page chrome (header/footer)
│   ├── styles.py            # ParagraphStyle construction
│   ├── components.py        # Flowable factories
│   └── convert/             # Markdown → JSON converter
│       ├── __init__.py      # Subpackage re-exports
│       ├── inline.py        # Inline markdown → XML
│       ├── frontmatter.py   # YAML frontmatter parser
│       ├── tables.py        # Pipe table parser
│       ├── blocks.py        # Block-level markdown parser
│       ├── sections.py      # Section builder
│       └── cli.py           # CLI entry point, orchestration
├── test/
│   ├── basic.md
│   ├── formatting.md
│   ├── tables.md
│   ├── code.md
│   ├── lists.md
│   ├── comprehensive.md
│   └── runner.py
├── docs/
│   └── CHANGELOG.md
├── AGENTS.md            # Agent context
├── TASKS.md             # Development backlog
└── pyproject.toml
```

## Design Decisions

- **ReportLab vs alternatives**: Chosen for not requiring Chrome, GTK, or TeX
- **Canvas + Platypus**: Canvas for chrome, Platypus for body content flow
- **Font naming**: `CustomSans-Bold` convention for TTF variant resolution
- **Link coloring**: Inline `<font color><u><a href>` due to ReportLab 5.x limitations
- **Two-pass rendering**: Required for TOC generation
- **System font detection**: Automatic Menlo registration on macOS for Unicode

## Known Limitations

- ReportLab 5.x ignores `linkColor` in ParagraphStyle (use inline styling)
- Courier fallback does not support Unicode box-drawing characters
- Images in markdown render as alt text only (use JSON schema for images)
- No nested list support (planned for future release)


## Contributing

Contributions are welcome! Please see TASKS.md for the current development backlog.


