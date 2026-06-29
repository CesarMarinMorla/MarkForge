# MarkForge — Contexto para Continuar

## Estado Actual

Proyecto maduro. Motor de PDF profesional desde JSON via ReportLab,
conversor determinista markdown → PDF. Sin LaTeX, sin Chrome, sin wkhtmltopdf.

## Pipeline

```
.md  ─►  markforge_convert.py  ─►  dict JSON  ─►  markforge/ (package)  ─►  .pdf
                 (determinista)       validate_content()
                                       build_theme() → C
                                       register_user_fonts() → F
                                       detect_system_mono()     ← macOS: Menlo
                                       build_styles(C, F) → S
                                       assemble_section()
                                       doc.multiBuild()
```

## Archivos

| Archivo | Rol |
|---|---|
| `markforge/` | Package modular (8 módulos) |
| `markforge/__init__.py` | Re-exporta `build_pdf`, `main` |
| `markforge/core.py` | `build_pdf()`, CLI `main()`, `resolve_page_size()` |
| `markforge/schema.py` | `validate_content()` — schema completo |
| `markforge/theme.py` | `build_theme()`, `DEFAULT_THEME` |
| `markforge/fonts.py` | `register_user_fonts()`, `detect_system_mono()`, `DEFAULT_FONTS` |
| `markforge/chrome.py` | `PageChrome` — header/footer/watermark canvas |
| `markforge/styles.py` | `build_styles()` — ParagraphStyles con colores y fonts |
| `markforge/components.py` | `safe_xml()`, `make_*()`, `assemble_section()` |
| `markforge/__main__.py` | `python -m markforge` entry point |
| `markforge_convert.py` | Conversor markdown determinista (~410 líneas) |
| `generate_pdf.py` | Entry point demo, wrapper de markforge_convert |
| `docs/CHANGELOG.md` | Historial de cambios |
| `test/` | Suite de tests sintéticos (6 archivos) |

## Dependencia

Solo `reportlab` (pip install reportlab).

## Lo Implementado

### Core Engine (markforge/)

- **Portada** con título, subtítulo, barra acento, tabla de metadatos
- **TOC** opcional via `show_toc: true` (multiBuild two-pass)
- **Secciones** con heading + regla horizontal de color
- **Body text** justificado, soporta `<b> <i> <br/> <a href> <sub> <super>`
- **Bullets** con prefijo `•` y left indent
- **Ordered lists** con prefijo `1. 2. 3.`
- **Highlight boxes** (call-out con borde izquierdo de color)
- **Tablas** con header repetido, filas alternadas, grid, col_widths proporcionales
- **Code blocks** (Preformatted, fondo gris, preserva indentación)
- **Imágenes** embedded con caption opcional
- **Watermark** diagonal semi-transparente en todas las páginas
- **Page break** forzado por sección (`page_break: true`)
- **Page size/orientation**: A4/Letter/Legal, portrait/landscape
- **Theming**: primary, accent, light, text, muted (hex colors)
- **Custom TTF fonts**: registro via `"fonts"` block en JSON, naming convention `CustomSans-Bold`
- **System font auto-detection**: En macOS, registra Menlo automáticamente como monospace (cubre Unicode)
- **Header/footer configurable**: `"header_footer"` block, placeholders `{page} {date} {title} {version}`
- **header.show=false**: topMargin se reduce de 2.2 cm a 1.0 cm para recuperar espacio
- **Schema validation**: `validate_content()` chequea todo el schema + rutas de archivo antes de renderizar
- **CLI**: `python -m markforge '<json>'` o `python markforge/core.py file.json`

### markforge_convert.py

- Parsea frontmatter YAML (Pandoc-style) → title, subtitle, author, date, toc, theme colors
- Inline markdown: `**bold**`, `*italic*`, `***bold italic***`, `` `code` ``, `[links](url)` → XML ReportLab
- Pipe tables → `table` schema con `col_widths` proporcionales
- Fenced code blocks ``` → `code` field (múltiples se unen con `\n\n`)
- Bullet lists (`- `) → `bullets` array
- Ordered lists (`1. `) → `ordered_list` array
- Blockquotes (`> `) → `highlight`
- Horizontal rules (`---`) → ignoradas
- Sub-headings (`###`-`######`) → bold en body text

## Test Suite

| Archivo | Cobertura |
|---|---|
| `test/basic.md` | Smoke test mínimo: cover, TOC, body text |
| `test/formatting.md` | Inline: bold, italic, links, code, accents, edge cases |
| `test/tables.md` | Pipe tables: vacías, single row, many columns, numérico |
| `test/code.md` | Code blocks: con/sin lenguaje, Unicode, múltiples por sección |
| `test/lists.md` | Bullets, ordered, single item, mixed con body |
| `test/comprehensive.md` | Todos los features combinados |

Uso: `python markforge_convert.py test/<file>.md`

## Schema JSON

```json
{
  "title":       "string (required)",
  "subtitle":    "string",
  "output":      "string",
  "page_size":   "A4 | Letter | Legal",
  "orientation": "portrait | landscape",
  "show_toc":    true,
  "show_cover":  true,
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

## Funciones Clave

| Función | Módulo | Qué hace |
|---|---|---|
| `validate_content(content)` | `schema.py` | Valida schema completo + rutas de archivo |
| `resolve_page_size(content)` | `core.py` | Retorna (width, height) en puntos |
| `build_theme(theme_config)` | `theme.py` | Mergea defaults con overrides |
| `safe_xml(text)` | `components.py` | Escapa `&` no-entity en texto |
| `register_user_fonts(fonts_config)` | `fonts.py` | Registra TTF + auto-detecta system fonts |
| `detect_system_mono()` | `fonts.py` | Busca Menlo en macOS, fallback Courier |
| `build_styles(C, F)` | `styles.py` | Construye ParagraphStyles con colores y fonts |
| `PageChrome` | `chrome.py` | Header/footer/watermark canvas por página |
| `make_cover(...)` | `components.py` | Portada flowable |
| `make_section_header(...)` | `components.py` | Heading + regla horizontal |
| `make_body(text, S)` | `components.py` | Párrafo body |
| `make_bullets(items, S)` | `components.py` | Lista de viñetas |
| `make_ordered_list(items, S)` | `components.py` | Lista numerada |
| `make_highlight(text, S, C, text_width)` | `components.py` | Call-out box |
| `make_image(img, S, text_width)` | `components.py` | Imagen embedded |
| `make_table(headers, rows, S, C, text_width, col_widths)` | `components.py` | Tabla con grid |
| `make_code(code_text, lang, C, text_width, mono_font)` | `components.py` | Code block Preformatted |
| `make_note(text, S)` | `components.py` | Nota italic muted |
| `assemble_section(section, S, C, text_width, toc, mono_font)` | `components.py` | Arma una sección completa |
| `build_pdf(content, output_path)` | `core.py` | Entry point principal |
| `main()` | `core.py` | CLI |

## Decisiones de Diseño Importantes

1. **ReportLab vs weasyprint/pdfkit/fpdf2**: ReportLab gana porque no necesita Chrome/GTK/TeX.
2. **Canvas + Platypus**: Canvas para chrome, Platypus para body content flow.
3. **Font naming convention**: `CustomSans-Bold` (con guión) para que `<b>` resuelva la variante TTF.
4. **Link coloring**: ReportLab 5.x ignora `linkColor`. Solución inline `<font color><u><a href>`.
5. **multiBuild two-pass**: TOC requiere multiBuild; callbacks de página corren dos veces.
6. **KeepTogether**: Heading + primer elemento juntos. Si el primero es muy alto, ReportLab lo parte igual.
7. **System font detection**: `detect_system_mono()` en macOS registra Menlo automáticamente para cubrir Unicode.
8. **topMargin dinámico**: Se reduce a 1.0 cm si `header.show=false`.
9. **inline_to_xml ordering**: `***text***` se procesa antes que `**text**`/`*text*` para evitar tag mismatch.

## Pitfalls Conocidos

- `footer.right` en `header_footer` tiene prioridad sobre `show_footer_date`.
- Font paths en `fonts` block validados en `validate_content()` pero errores de registro TTF se silencian.
- Image path inexistente → renderiza "[Image not found: path]".
- `None` en celda de tabla → convertido a `""` por `_cell_text()`.
- Para TOC, `show_cover=false` + `show_toc=true` funciona bien.
- Fecha auto-add solo detecta keys "date", "fecha", "datum".
- Sub-headings (`###`-`######`) van como bold en body, no como secciones separadas.
- Courier es el último recurso si `detect_system_mono()` falla (no cubre Unicode).
- El monstruo original `pdf_engine.py` vive en git: `git show d62b08d^:pdf_engine.py`

## Convenciones

- El engine está documentado en inglés para agentes
- Los mensajes de commit están en inglés, formato Conventional Commits
- La conversación con el usuario fue en español
- `generate_pdf.py` es el entry point demo; `markforge_convert.py` es el pipeline determinista
- Sin tags de version
