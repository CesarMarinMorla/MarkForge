# Changelog

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

## v1.0.0 (2026-06-25)

Primera versión estable del **Agent PDF Engine**. Motor determinista para generacion de PDF profesional a partir de JSON, usando ReportLab Platypus.

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
python pdf_engine.py '{"title":"Doc","sections":[{"heading":"S1","body":"..."}]}'
python pdf_engine.py path/to/content.json
python pdf_engine.py path/to/content.json output.pdf
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

- Courier no soporta Unicode: usar solo ASCII para bloques de codigo (sin ├ ─ │ → ↓)
- `linkColor` en ParagraphStyle es ignorado por ReportLab 5.x: usar `<font color>` inline
- Ordered lists no soportadas: simular con bullets manuales tipo `"1. item"`
- Sin form fields, sin validacion estricta de schema (JSON malformado da errores de Python crudos)
