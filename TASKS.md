# MarkForge — Task Backlog

Prioridades: **P1** (core engine), **P2** (quality & packaging), **P3** (polish), **P4** (long term)

---

## P1 — Engine Features (markdown converter)

- [x] **Inline monospace in body** — `` `code` `` strips backticks but renders in body font. Wrap with `<tt>` or `<font face="mono">` to use the registered monospace font.
- [x] **Inline code formatting** — fenced code blocks as Preformatted, inline `` `code` `` with rounded gray background.
- [x] **Section numbering** — auto-generate `1.`, `1.1`, `1.2` from heading nesting (`##` → level 1, `###` → level 2). Configurable via frontmatter `number_sections: true`.
- [ ] **Image rendering from markdown** — `![alt](path)` currently converts to alt text only. Pipe through `make_image()` flowable if path exists.
- [x] **Handle `# ` level 1 headings** — treated as section boundary (same as `## `). Falls through to body text in sections.
- [ ] **Task lists** — `- [ ]` / `- [x]` syntax rendered as checkboxes in PDF.
- [ ] **Nested lists** — sub-bullets with indentation (multi-level bullets and ordered lists).
- [x] **Multiple blockquotes per section** — already works via `blocks` path (`_render_blocks`).
- [ ] **Definition lists** — `term\n: definition` Pandoc syntax.

## P1 — Engine Features (rendering)

- [ ] **Image alignment** — `make_image()` centers. Support `left`, `right`, `center` via `align` field or markdown attribute.
- [ ] **Custom margins per section** — each section dict accepts `top_margin`, `bottom_margin`, `left_margin`, `right_margin`.
- [ ] **SVG support** — convert SVG to raster (cairosvg) or inline as vector PDF.
- [x] **Table caption** — optional caption detected from `Table: ...` line before pipe table.
- [ ] **Table styling** — per-column colors, custom header background, stripe pattern config.

## P2 — CLI & Packaging

- [ ] **`pyproject.toml`** — project metadata, dependencies, `[project.scripts]` entry point.
- [ ] **`markforge/cli.py`** — unify CLI: `markforge doc.md`, `markforge content.json`, `-o` flag, glob, stdin.
- [ ] **`python -m markforge`** — delegate to `cli.py`.
- [ ] **`generate_pdf.py` deprecation** — remove once CLI is stable.
- [ ] **Rich CLI output** — progress, colored errors.

## P2 — Testing & Quality

- [x] **PDF content validation in runner** — decode PDF streams and check expected strings per test (TOC entries, index entries, body text). Replaces crash-only check.
- [x] **Integration test** — full pipeline for every file in `test/`.
- [ ] **Unit tests (pytest)** — core functions: `build_pdf`, `validate_content`, `register_user_fonts`, `build_styles`, `build_theme`, `inline_to_xml`, `build_sections`, `parse_pipe_table`, `parse_code_block`.
- [ ] **Fixture PDF comparison** — generate expected PDFs, compare page count/metadata.
- [ ] **`blocks` array validation in schema.py** — validate typed block objects inside sections, not just flat fields.
- [ ] **`validate_content()` unit tests** — test with invalid inputs: missing title, empty sections, bad image paths, malformed JSON, etc.
- [ ] **Property-based tests** — random content dicts with hypothesis.
- [ ] **Type hints** — cover all public functions.
- [ ] **Static analysis** — ruff linter + pyright type checker.

## P2 — Documentation

- [ ] **`docs/architecture.md`** — module dependency graph, data flow.
- [ ] **`docs/usage.md`** — examples: basic, custom fonts, header/footer, theming.
- [ ] **`docs/development.md`** — setup, test runner, conventions.
- [ ] **`README.md`** — project overview, quick start, badges.

## P3 — Polish & Performance

- [ ] **Multi-column layouts** — 2/3 column body sections via Platypus frames.
- [ ] **Page numbering formats** — `- 1 -`, `Page 1 of N`, roman numerals.
- [ ] **Watermark config** — opacity, rotation, size, per-page control.
- [ ] **Template system** — reusable JSON fragments for headers/footers/fonts.
- [ ] **Parallel build** — multiprocessing for batch generation.
- [ ] **Streaming output** — generate PDF to BytesIO for web apps.
- [ ] **PDF metadata** — title, author, subject, keywords via document info.
- [ ] **PDF/A compliance** — archival-grade output.

## P4 — GUI & Integration

- [ ] **Web UI** — Flask/FastAPI server, accept markdown/JSON, return PDF.
- [ ] **Desktop GUI** — Tkinter/Qt visual document builder.
- [ ] **VS Code extension** — preview PDF from markdown in-editor.
- [ ] **Markdown preview** — side-by-side editor + PDF renderer.

---

## Known Bugs

- [ ] `linkColor` in ParagraphStyle ignored by ReportLab 5.x (use inline `<font color>`)
- [ ] Courier fallback does not support Unicode box-drawing (mitigated by Menlo on macOS)

---

## Changelog

| Date | Note |
|---|---|
| 2026-06-29 | Created. Repo at v1.2.0 after cleanup/rename session. |
| 2026-06-30 | Runner validates PDF content; `#` headings as sections; TOC dots fix; index + TOC headings; preamble fix. |
