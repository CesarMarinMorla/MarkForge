# Changelog

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
- Sin watermarks, sin form fields, sin custom fonts via schema
- Sin validacion estricta de schema (JSON malformado da errores de Python crudos)
