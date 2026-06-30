# Changelog

## v0.3.0 (2026-06-29)

Refactor to modular package and Phase 1 polish.

- **Modular package**: `markforge/` replaces the 1700-line monolith.
  8 submodules with explicit dependencies. Backward compatible.
- **detect_system_mono()**: on macOS detects and registers Menlo automatically
  as the default monospace. Covers Unicode (box-drawing, arrows, Latin accents).
  Courier is no longer the default; if Menlo is unavailable, falls back to Courier.
- **Dynamic topMargin**: reduced to 1.0 cm when `header.show=false`.
- **Custom fonts in PageChrome**: header, footer and watermark use registered
  fonts instead of hardcoded Helvetica.
- **image_caption style**: added to `build_styles()` with the registered italic
  font instead of hardcoded `Helvetica-Oblique`.
- **Inline code formatting**: `make_code()` renders fenced code blocks as `Preformatted` with gray background; inline `` `code` `` spans use monospace font with rounded `roundRect` background via monkey-patched `_do_post_text`.
- **Multiple code blocks/tables in markforge_convert**: code blocks joined with `\n\n`,
  extra tables rendered as body text instead of being discarded.
- **Path validation**: `validate_content()` checks that font and image files
  exist before rendering.
- **Automatic col_widths**: proportional to header length instead of equal.
- **None defense in tables**: helper `_cell_text()` normalizes any non-string
  cell to `""` to prevent crashes.
- **__main__.py**: `python -m markforge` now works as entry point.

## v0.2.0 (2026-06-25)

Custom fonts via JSON schema. Atkinson Hyperlegible + JetBrains Mono demo.
Header/footer configurable content.

- **Custom fonts**: `"fonts"` block in JSON registers TTF files via ReportLab's
  pdfmetrics/TTFont. Roles (`sans`, `mono`, `serif`) map to style sheet;
  missing paths fall back to Helvetica/Courier/Times built-ins.
- **register_user_fonts()**: merges user TTF config with DEFAULT_FONTS, returns
  a role -> (regular, bold, italic, bold_italic) tuple dict.
- **Dash naming convention**: fonts are registered with dash suffixes
  (CustomSans-Bold, CustomSans-Italic, CustomSans-BoldItalic) so inline XML
  `<b>`/`<i>` resolve to the correct TTF variant. Registering without dash
  (CustomSansBold) silently falls back to synthetic bold/italic.
- **build_styles(C, F)**: all ParagraphStyles now source fontName from the `F`
  dict (sans_reg, sans_bold, sans_ital, etc.) instead of hardcoded Helvetica.
- **make_code(mono_font)**: accepts optional mono_font parameter (default Courier)
  from F["mono"][0] so custom monospace fonts apply to code blocks.
- **assemble_section(mono_font)**: threads mono_font through to make_code().
- **Migrated demo** from variable fonts (Source Sans 3 / Source Code Pro) to
  static-weight Atkinson Hyperlegible (designed for maximum legibility by
  Braille Institute) and JetBrains Mono. Variable fonts render too thin because
  ReportLab reads their default lightweight axis value.
- **Header/footer configurable**: `"header_footer"` block in JSON overrides
  header left/right, footer left/center/right, and show/hide flags. Placeholders
  `{page}`, `{date}`, `{title}`, `{version}` resolve at render time. Fully
  backward-compatible with existing `show_footer_date`.
- **Schema validation**: `validate_content()` checks the full JSON schema at
  build time and raises ValueError with ALL errors found (types, required fields,
  hex colors, table structure). File paths are NOT validated.
- **Ordered lists**: `make_ordered_list()` renders numbered lists via `Paragraph` with numbered prefix, left indent, and proper spacing.
- **markforge_convert.py**: Deterministic markdown-to-PDF converter. Parses Pandoc YAML
  frontmatter, converts inline formatting, pipe tables, fenced code blocks,
  bullet/ordered lists, and blockquotes to the engine's JSON schema. No AI
  required. Usage: `python markforge_convert.py doc.md [output.pdf]`.
- **generate_pdf.py**: Simplified to a thin wrapper around markforge_convert.convert().

## v0.1.0 (2026-06-25)

First stable release of **MarkForge** (formerly Agent PDF Engine). Deterministic engine for professional PDF generation from JSON, using ReportLab Platypus.

### Features

- **Cover page** with title, subtitle, accent color bar and metadata table
- **Table of Contents (TOC)** optional via `show_toc: true`
- **Sections** with heading separated by colored horizontal rule
- **Body text** justified with inline XML support (`<b>`, `<i>`, `<br/>`, `<a href>`)
- **Bullets** with bullet prefix and left indent
- **Highlight boxes** with colored left border (call-outs)
- **Tables** with header repeated on each page, alternating rows, grid
- **Code blocks** in Courier with gray background, preserving indentation (Preformatted)
- **Embedded images** with optional caption
- **Footnotes** in italic muted
- **Clickable links** with accent color and underline (`<font color><u><a href>`)
- **Automatic meta**: if no date is provided, uses current date; recognizes `date`
- **Page size**: A4 (default), Letter, Legal; orientation portrait/landscape
- **Customizable theme**: primary, accent, light, text, muted (hex colors in JSON)
- **Cover control**: `show_cover: false` omits it
- **Footer control**: `show_footer_date: false` hides the generation date
- **Configurable output path** from JSON or second CLI argument

### CLI

```bash
pip install reportlab
python -m markforge '{"title":"Doc","sections":[{"heading":"S1","body":"..."}]}'
python -m markforge path/to/content.json
python -m markforge path/to/content.json output.pdf
```

### Architecture

- `build_theme()` -- merges defaults with JSON overrides
- `build_styles()` -- generates ParagraphStyles with theme colors
- `PageChrome` -- header bar + footer (page number, date)
- `make_cover()`, `make_section_header()`, `make_body()`, `make_bullets()`, `make_highlight()`, `make_image()`, `make_code()`, `make_table()`, `make_note()` -- builders that return lists of Flowables
- `assemble_section()` -- builds a complete section with KeepTogether to prevent orphan headings
- `build_pdf()` -- main entry point
- `main()` -- CLI that accepts JSON string or path to file

### Known Limitations

- Courier does not support Unicode: use only ASCII for code blocks (no ├ ─ │ -> down) -- resolved in v0.3.0 (Menlo auto-detect)
- `linkColor` in ParagraphStyle is ignored by ReportLab 5.x: use `<font color>` inline
- Ordered lists not supported -- resolved in v0.2.0
- No form fields -- resolved in v0.2.0 (schema validation)
