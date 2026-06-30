# MarkForge — Context for Continuation

## Current State

Mature project. Professional PDF engine from JSON via ReportLab,
deterministic markdown -> PDF converter. No LaTeX, no Chrome, no wkhtmltopdf.

## Pipeline

```
.md  ->  markforge/convert/  ->  dict JSON  ->  markforge/ (package)  ->  .pdf
                (deterministic)    validate_content()
                                   build_theme() -> C
                                   register_user_fonts() -> F
                                   detect_system_mono()     <- macOS: Menlo
                                   build_styles(C, F) -> S
                                   assemble_section()
                                   doc.multiBuild()
```

## Files

| File | Role |
|---|---|
| `markforge/` | Modular package (8 modules) |
| `markforge/convert/` | Markdown -> dict converter subpackage (6 modules) |
| `markforge/__init__.py` | Re-exports `build_pdf`, `main` |
| `markforge/core.py` | `build_pdf()`, CLI `main()`, `resolve_page_size()` |
| `markforge/schema.py` | `validate_content()` -- full schema |
| `markforge/theme.py` | `build_theme()`, `DEFAULT_THEME` |
| `markforge/fonts.py` | `register_user_fonts()`, `detect_system_mono()`, `DEFAULT_FONTS` |
| `markforge/chrome.py` | `PageChrome` -- header/footer/watermark canvas |
| `markforge/styles.py` | `build_styles()` -- ParagraphStyles with colors and fonts |
| `markforge/components.py` | `safe_xml()`, `make_*()`, `assemble_section()` |
| `markforge/__main__.py` | `python -m markforge` entry point |
| `test/runner.py` | Test runner -- runs all test/*.md |
| `docs/CHANGELOG.md` | Change history |
| `test/` | Synthetic test suite (6 files) |

## Dependencies

Only `reportlab` (pip install reportlab).

## Implemented

### Core Engine (markforge/)

- **Cover page** with title, subtitle, accent bar, metadata table
- **TOC** optional via `show_toc: true` (multiBuild two-pass). Includes heading "Table of Contents", dotted leaders (`.`), HR separator at end
- **Index** optional via `show_index: true` (SimpleIndex, <<term>> in md). Includes heading "Index", appears in TOC
- **Sections** with heading + colored horizontal rule
- **Body text** justified, supports `<b> <i> <br/> <a href> <sub> <super>`
- **Bullets** with `•` prefix and left indent
- **Ordered lists** with `1. 2. 3.` prefix
- **Highlight boxes** (call-out with colored left border)
- **Tables** with repeated header, alternating rows, grid, proportional col_widths
- **Inline code blocks** (Preformatted, gray background, preserves indentation)
- **Inline code spans** (`...`) with rounded light gray background, monospace font, pad=1.5 horizontal, vpad=0.5 vertical
- **Images** embedded with optional caption
- **Watermark** diagonal semi-transparent on all pages
- **Page break** forced per section (`page_break: true`)
- **Page size/orientation**: A4/Letter/Legal, portrait/landscape
- **Theming**: primary, accent, light, text, muted (hex colors)
- **Custom TTF fonts**: registration via `"fonts"` block in JSON, naming convention `CustomSans-Bold`
- **System font auto-detection**: On macOS, registers Menlo automatically as monospace (covers Unicode)
- **Header/footer configurable**: `"header_footer"` block, placeholders `{page} {date} {title} {version}`
- **header.show=false**: topMargin reduces from 2.2 cm to 1.0 cm to reclaim space
- **Schema validation**: `validate_content()` checks full schema + file paths before rendering
- **CLI**: `python -m markforge '<json>'` or `python markforge/core.py file.json`

### markforge/convert/ (subpackage)

- Parses YAML frontmatter (Pandoc-style) -> title, subtitle, author, date, toc, theme colors
- Inline markdown: `**bold**`, `*italic*`, `***bold italic***`, `` `code` ``, `[links](url)` -> ReportLab XML
- Pipe tables -> `table` schema with proportional `col_widths`
- Fenced code blocks ``` -> `code` field (multiple joined with `\n\n`)
- Bullet lists (`- `) -> `bullets` array
- Ordered lists (`1. `) -> `ordered_list` array
- Blockquotes (`> `) -> `highlight`
- Horizontal rules (`---`) -> ignored
- `#`/`##` headings -> section boundaries (creates new section)
- Sub-headings (`###`-`######`) -> bold in body text
- Index terms (`<<term>>`) -> `<index item="term"/>` for alphabetical index

## Test Suite

| File | Coverage |
|---|---|
| `test/basic.md` | Minimum smoke test: cover, TOC, body text |
| `test/formatting.md` | Inline: bold, italic, links, code, accents, edge cases |
| `test/tables.md` | Pipe tables: empty, single row, many columns, numeric |
| `test/code.md` | Code blocks: with/without language, Unicode, multiple per section |
| `test/lists.md` | Bullets, ordered, single item, mixed with body |
| `test/comprehensive.md` | All features combined |

Usage: `python test/runner.py` for all or `python -m markforge.convert test/<file>.md` for one

## Schema JSON

```json
{
  "title":       "string (required)",
  "subtitle":    "string",
  "output":      "string",
  "page_size":   "A4 | Letter | Legal",
  "orientation": "portrait | landscape",
  "show_toc":     true,
  "show_index":   true,
  "show_cover":   true,
  "show_footer_date": true,
  "watermark":   "string",
  "fonts": {
    "sans":  { "regular": "path", "bold": "path", "italic": "path", "bold_italic": "path" },
    "mono":  { "regular": "path", "bold": "path" },
    "serif": { "regular": "path", ... }
  },
  "header_footer": {
    "header": { "show": true, "left": "string", "right": "string" },
    "footer": { "show": true, "left": "string", "center": "string", "right": "string" }
  },
  "theme": {
    "primary": "#RRGGBB", "accent": "#RRGGBB",
    "light": "#RRGGBB",   "text": "#RRGGBB", "muted": "#RRGGBB"
  },
  "meta": { "key": "value", ... },
  "sections": [
    {
      "heading": "string (required per section)",
      "body": "string (with XML inline tags)",
      "bullets": ["string", ...],
      "ordered_list": ["string", ...],
      "highlight": "string",
      "image": { "path": "string", "width": float, "height": float, "caption": "string" },
      "code": "string",
      "language": "string",
      "table": {
        "headers": ["col1", "col2", ...],
        "rows": [["cell1", "cell2"], ...],
        "col_widths": [float, float, ...]
      },
      "page_break": true,
      "note": "string"
    }
  ]
}
```

## Key Functions

| Function | Module | What it does |
|---|---|---|
| `validate_content(content)` | `schema.py` | Validates full schema + file paths |
| `resolve_page_size(content)` | `core.py` | Returns (width, height) in points |
| `build_theme(theme_config)` | `theme.py` | Merges defaults with overrides |
| `safe_xml(text)` | `components.py` | Escapes non-entity `&` in text |
| `register_user_fonts(fonts_config)` | `fonts.py` | Registers TTF + auto-detects system fonts |
| `detect_system_mono()` | `fonts.py` | Looks for Menlo on macOS, fallback Courier |
| `build_styles(C, F)` | `styles.py` | Builds ParagraphStyles with colors and fonts |
| `PageChrome` | `chrome.py` | Header/footer/watermark canvas per page |
| `make_cover(...)` | `components.py` | Cover page flowable |
| `make_section_header(...)` | `components.py` | Heading + horizontal rule |
| `make_body(text, S)` | `components.py` | Body paragraph |
| `make_bullets(items, S)` | `components.py` | Bullet list |
| `make_ordered_list(items, S)` | `components.py` | Numbered list |
| `make_highlight(text, S, C, text_width)` | `components.py` | Call-out box |
| `make_image(img, S, text_width)` | `components.py` | Embedded image |
| `make_table(headers, rows, S, C, text_width, col_widths)` | `components.py` | Table with grid |
| `make_code(code_text, lang, C, text_width, mono_font)` | `components.py` | Code block Preformatted |
| `make_note(text, S)` | `components.py` | Italic muted note |
| `make_index(F, C, text_width)` | `components.py` | Alphabetical SimpleIndex |
| `parse_content_blocks(lines, accent, mono_font)` | `convert/blocks.py` | Parses markdown lines -> blocks dict |
| `assemble_section(section, S, C, text_width, toc, mono_font)` | `components.py` | Builds a complete section |
| `build_pdf(content, output_path)` | `core.py` | Main entry point |
| `main()` | `core.py` | CLI |

## Important Design Decisions

1. **ReportLab vs weasyprint/pdfkit/fpdf2**: ReportLab wins because it doesn't need Chrome/GTK/TeX.
2. **Canvas + Platypus**: Canvas for chrome, Platypus for body content flow.
3. **Font naming convention**: `CustomSans-Bold` (with dash) so `<b>` resolves the TTF variant.
4. **Link coloring**: ReportLab 5.x ignores `linkColor`. Solution: inline `<font color><u><a href>`.
5. **multiBuild two-pass**: TOC requires multiBuild; page callbacks run twice.
6. **KeepTogether**: Heading + first element together. If the first is too tall, ReportLab splits it anyway.
7. **_tocInfo propagation**: `_tocInfo` is set on the heading `Paragraph`, but `assemble_section` wraps it in `KeepTogether`. `afterFlowable` only sees the `KeepTogether`, so `_tocInfo` must be propagated explicitly to the wrapper. Otherwise the TOC never receives entries.
8. **System font detection**: `detect_system_mono()` on macOS registers Menlo automatically to cover Unicode.
9. **Dynamic topMargin**: Reduced to 1.0 cm if `header.show=false`.
10. **inline_to_xml ordering**: `***text***` is processed before `**text**`/`*text*` to avoid tag mismatch.

## Known Pitfalls

- `footer.right` in `header_footer` takes priority over `show_footer_date`.
- Font paths in `fonts` block validated in `validate_content()` but TTF registration errors are silenced.
- Non-existent image path -> renders "[Image not found: path]".
- `None` in table cell -> converted to `""` by `_cell_text()`.
- For TOC, `show_cover=false` + `show_toc=true` works fine.
- Date auto-add only detects key "date".
- Sub-headings (`###`-`######`) go as bold in body, not as separate sections.
- Courier is the last resort if `detect_system_mono()` fails (doesn't cover Unicode).
- Index requires custom `canvasmaker` in `multiBuild` to register `<index item="term"/>` callbacks.
- The TOC heading "Table of Contents" does NOT have `_tocInfo` (avoids circular reference). The Index heading does have `_tocInfo` and appears in the TOC.
- `dotsMinLevel` of the TOC must match the level of `_tocInfo` (both at 0) for dotted leaders to render.
- Preamble content (before the first `## heading`) was silently discarded. Now `parse_content_blocks()` processes it and prepends it to the first section.
- The original `pdf_engine.py` monolith lives in git: `git show d62b08d^:pdf_engine.py`

## Conventions

- The engine is documented in English for agents
- Commit messages are in English, Conventional Commits format
- `test/runner.py` runs all tests; `markforge/convert/` is the deterministic pipeline
- No version tags