# Changelog

## v1.2.0 (2026-06-29)

Refactor a package modular y Fase 1 de pulido.

- **Package modular**: `markforge/` reemplaza al monolito de 1700 líneas.
  8 submódulos con dependencias explícitas. Backward compatible.
- **detect_system_mono()**: en macOS detecta y registra Menlo automáticamente
  como monospace default. Cubre Unicode (box-drawing, flechas, acentos latinos).
  Courier ya no es el default; si Menlo no está disponible, cae a Courier.
- **topMargin dinámico**: se reduce a 1.0 cm cuando `header.show=false`.
- **Font custom en PageChrome**: header, footer y watermark usan los fonts
  registrados en vez de Helvetica hardcoded.
- **image_caption style**: agregado a `build_styles()` con el font itálico
  registrado en vez de `Helvetica-Oblique` hardcoded.
- **Inline code formatting**: `make_code()` renders fenced code blocks as `Preformatted` with gray background; inline `` `code` `` spans use monospace font with rounded `roundRect` background via monkey-patched `_do_post_text`.
- **Múltiples code blocks/tables en markforge_convert**: code blocks se unen con `\n\n`,
  tablas extra se renderizan como body text en vez de descartarse.
- **Validación de rutas**: `validate_content()` chequea que existan archivos
  de fonts e imágenes antes de renderizar.
- **col_widths automática**: proporcional al largo del header en vez de igual.
- **Defensa None en tablas**: helper `_cell_text()` normaliza cualquier celda
  no-string a `""` para evitar crashes.
- **__main__.py**: `python -m markforge` ahora funciona como entry point.

## v1.1.0 (2026-06-25)

Custom fonts via JSON schema. Atkinson Hyperlegible + JetBrains Mono demo.
Header/footer configurable content.

- **Custom fonts**: `"fonts"` block in JSON registers TTF files via ReportLab's
  pdfmetrics/TTFont. Roles (`sans`, `mono`, `serif`) map to style sheet;
  missing paths fall back to Helvetica/Courier/Times built-ins.
- **register_user_fonts()**: merges user TTF config with DEFAULT_FONTS, returns
  a role → (regular, bold, italic, bold_italic) tuple dict.
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

## v1.0.0 (2026-06-25)

Primera versión estable de **MarkForge** (entonces Agent PDF Engine). Motor determinista para generacion de PDF profesional a partir de JSON, usando ReportLab Platypus.

### Features

- **Portada** con titulo, subtitulo, barra de acento color y tabla de metadatos
- **Tabla de Contenidos (TOC)** opcional via `show_toc: true`
- **Secciones** con heading separado por regla horizontal de color
- **Cuerpo de texto** justificado con soporte de inline XML (`<b>`, `<i>`, `<br/>`, `<a href>`)
- **Vinetas** con prefijo bullet y left indent
- **Highlight boxes** con borde izquierdo de color (call-outs)
- **Tablas** con cabecera repetida en cada pagina, filas alternadas, grid
- **Bloques de codigo** en Courier con fondo gris, preservando indentacion (Preformatted)
- **Imagenes** incrustadas con caption opcional
- **Notas al pie** en italica muted
- **Links clickeables** con color accent y underline (`<font color><u><a href>`)
- **Meta automatico**: si no se provee fecha, se usa la actual; reconoce `date`, `fecha`, `datum`
- **Page size**: A4 (default), Letter, Legal; orientation portrait/landscape
- **Tema customizable**: primary, accent, light, text, muted (hex colors en JSON)
- **Control de portada**: `show_cover: false` la omite
- **Control de footer**: `show_footer_date: false` oculta la fecha de generacion
- **Output path** configurable desde JSON o segundo argumento CLI

### CLI

```bash
pip install reportlab
python -m markforge '{"title":"Doc","sections":[{"heading":"S1","body":"..."}]}'
python -m markforge path/to/content.json
python -m markforge path/to/content.json output.pdf
```

### Arquitectura

- `build_theme()` — fusiona defaults con overrides del JSON
- `build_styles()` — genera ParagraphStyles con colores del tema
- `PageChrome` — header bar + footer (numero de pagina, fecha)
- `make_cover()`, `make_section_header()`, `make_body()`, `make_bullets()`, `make_highlight()`, `make_image()`, `make_code()`, `make_table()`, `make_note()` — builders que retornan listas de Flowables
- `assemble_section()` — arma una seccion completa con KeepTogether anti-headings huerfanos
- `build_pdf()` — entry point principal
- `main()` — CLI que acepta JSON string o path a archivo

### Limitaciones conocidas

- Courier no soporta Unicode: usar solo ASCII para bloques de codigo (sin ├ ─ │ → ↓) — resuelto en v1.2.0 (Menlo auto-detect)
- `linkColor` en ParagraphStyle es ignorado por ReportLab 5.x: usar `<font color>` inline
- Ordered lists no soportadas — resuelto en v1.1.0
- Sin form fields — resuelto en v1.1.0 (schema validation)
