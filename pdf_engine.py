"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              AGENT PDF ENGINE  —  Full Reference & Implementation           ║
║                                                                              ║
║  This file is the canonical PDF generation backend for AI agents.           ║
║  It is intentionally over-documented so any agent can read it, understand   ║
║  every decision, and extend or adapt it without guesswork.                  ║
║                                                                              ║
║  INSTALL:   pip install reportlab                                            ║
║  USAGE:     python pdf_engine.py '{"title":"My Report", ...}'               ║
║             python pdf_engine.py path/to/content.json                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY REPORTLAB AND NOT SOMETHING ELSE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Option          Pros                         Cons / Disqualifiers
  ─────────────── ──────────────────────────── ────────────────────────────────
  reportlab       Mature, full control, no      Verbose API
  (THIS FILE)     headless browser needed,
                  pure Python, battle-tested

  weasyprint      HTML→PDF, easier styling      Requires GTK/Cairo, fragile
                                                in containers

  pdfkit/wkhtmlto HTML→PDF                      Needs wkhtmltopdf binary,
  pdf                                           abandoned upstream

  fpdf2           Simple API                    Limited table/flow support

  LaTeX           Perfect typography            Requires full TeX install,
                                                not agent-friendly

  VERDICT: reportlab's Platypus layout engine is the best fit for agents
  generating structured documents (reports, invoices, specs). Use weasyprint
  only if you're already generating HTML and want CSS-based styling.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPORTLAB CORE CONCEPTS (read this before touching the code below)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. CANVAS vs PLATYPUS
     ─────────────────────
     ReportLab has two layers:

     • canvas (low-level): You place every element at exact (x, y) coordinates.
       The coordinate origin is BOTTOM-LEFT of the page. Y increases upward.
       Use for: headers/footers, watermarks, custom shapes, form fields.
       ⚠ DO NOT use canvas for body content — you'd have to track y-position
         manually and handle page breaks yourself.

     • Platypus (high-level): A layout engine. You build a "story" — an ordered
       list of Flowable objects. Platypus handles line-wrapping, pagination,
       column flow, table layout, and spacing automatically.
       Use for: ALL body content (paragraphs, tables, lists, images).

     This engine uses BOTH: canvas for per-page chrome (header bar, footer),
     Platypus for the document body.

  2. FLOWABLES
     ──────────
     Every Platypus content element is a Flowable. Key ones:

     • Paragraph(text, style)       — Wrapped, styled text. Supports inline XML
                                      markup: <b>, <i>, <font>, <br/>, <sub>,
                                      <super>, <a href="...">.
     • Spacer(width, height)        — Vertical whitespace. Width is ignored for
                                      single-column; use 1 as a placeholder.
     • Table(data, colWidths, style)— Grid layout. data is list-of-lists of
                                      strings OR Flowables. Always provide
                                      colWidths explicitly for predictability.
     • HRFlowable(...)              — Horizontal rule / divider line.
     • PageBreak()                  — Forces a new page in the story.
     • KeepTogether([f1, f2, ...])  — Wraps multiple flowables so they're never
                                      split across a page break (e.g., heading
                                      + first paragraph of a section).
     • Image(path, width, height)   — Embedded image. Scale explicitly.

  3. PARAGRAPH INLINE MARKUP
     ─────────────────────────
     Paragraph text is XML. Special characters must be escaped:
       & → &amp;    < → &lt;    > → &gt;
     Supported tags:
       <b>bold</b>                 <i>italic</i>
       <u>underline</u>            <strike>strikethrough</strike>
       <font name="..." size="..." color="...">text</font>
       <sub>subscript</sub>        <super>superscript</super>
       <br/>                       (line break within paragraph)
       <a href="url">link</a>
     ⚠ NEVER use Unicode sub/superscripts (₂, ³, etc.) — built-in fonts lack
       these glyphs; they render as solid black rectangles.

  4. PARAGRAPHSTYLE PROPERTIES
     ────────────────────────────
     fontName      — Must be one of the 14 built-in PDF fonts:
                       Helvetica, Helvetica-Bold, Helvetica-Oblique,
                       Helvetica-BoldOblique, Times-Roman, Times-Bold,
                       Times-Italic, Times-BoldItalic, Courier, Courier-Bold,
                       Courier-Oblique, Courier-BoldOblique, Symbol, ZapfDingbats
                     OR a registered TTF font (see registerFont below).
     fontSize      — In points (pt). 1pt = 1/72 inch.
     leading       — Line height in points. Rule of thumb: fontSize × 1.2–1.5.
     textColor     — colors.Color object or colors.HexColor("#RRGGBB").
     alignment     — TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY.
     spaceBefore   — Vertical space above paragraph, in points.
     spaceAfter    — Vertical space below paragraph, in points.
     leftIndent    — Left margin indent from the text frame, in points.
     rightIndent   — Right margin indent, in points.
     firstLineIndent — Extra indent for first line only.
     bulletIndent  — Where the bullet character sits (left of leftIndent).
     bulletText    — The bullet character (e.g., "•"). Set on style for lists.
     backColor     — Background fill color for the paragraph box.
     borderColor   — Border color (use with borderWidth, borderPadding).
     wordWrap      — "CJK" for CJK text, otherwise leave unset.

  5. TABLE STYLE COMMANDS
     ──────────────────────
     TableStyle takes a list of (command, start_cell, end_cell, *args) tuples.
     Cell coordinates are (col, row), 0-indexed. (-1, -1) means last cell.
     Common commands:
       ("BACKGROUND",   (c1,r1), (c2,r2), color)
       ("TEXTCOLOR",    (c1,r1), (c2,r2), color)
       ("FONT",         (c1,r1), (c2,r2), fontName, fontSize)
       ("FONTNAME",     (c1,r1), (c2,r2), fontName)
       ("FONTSIZE",     (c1,r1), (c2,r2), size)
       ("ALIGN",        (c1,r1), (c2,r2), "LEFT"|"CENTER"|"RIGHT")
       ("VALIGN",       (c1,r1), (c2,r2), "TOP"|"MIDDLE"|"BOTTOM")
       ("GRID",         (c1,r1), (c2,r2), lineWidth, color)
       ("BOX",          (c1,r1), (c2,r2), lineWidth, color)
       ("LINEABOVE",    (c1,r1), (c2,r2), lineWidth, color)
       ("LINEBELOW",    (c1,r1), (c2,r2), lineWidth, color)
       ("LINEBEFORE",   (c1,r1), (c2,r2), lineWidth, color)
       ("LINEAFTER",    (c1,r1), (c2,r2), lineWidth, color)
       ("TOPPADDING",   (c1,r1), (c2,r2), points)
       ("BOTTOMPADDING",(c1,r1), (c2,r2), points)
       ("LEFTPADDING",  (c1,r1), (c2,r2), points)
       ("RIGHTPADDING", (c1,r1), (c2,r2), points)
       ("SPAN",         (c1,r1), (c2,r2))   ← merge cells
       ("ROWBACKGROUNDS",(c1,r1),(c2,r2), [color1, color2])  ← alternating rows
     Table also accepts: repeatRows=N (repeat first N rows as header on each page)

  6. UNITS
     ───────
     All ReportLab dimensions are in POINTS (pt) by default.
     Import helpers: from reportlab.lib.units import cm, mm, inch
     1 inch = 72 pt    1 cm = 28.35 pt    1 mm = 2.835 pt

  7. PAGE TEMPLATE HOOKS
     ─────────────────────
     SimpleDocTemplate.build(story, onFirstPage=fn, onLaterPages=fn)
     Both callbacks receive (canvas, doc). Use them for per-page chrome.
     doc.page gives the current page number (1-indexed).
     doc.pagesize gives (width, height).
     Always call canvas.saveState() at the start and canvas.restoreState()
     at the end of these callbacks to avoid leaking state into Platypus.

  8. COORDINATE SYSTEM IN CANVAS CALLBACKS
     ─────────────────────────────────────────
     Origin (0,0) is BOTTOM-LEFT. Y increases UPWARD.
     So to draw something near the TOP of an A4 page (height ≈ 841 pt):
       y = PAGE_H - 1.5*cm   ← 1.5 cm from top
     And near the BOTTOM:
       y = 1.0*cm             ← 1 cm from bottom

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT SCHEMA (what the agent must produce as JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{
  "title":    string,          REQUIRED. Main document title. Appears on the
                               cover page (large) and in every page header.

  "subtitle": string,          OPTIONAL. Supporting subtitle on cover page only.

  "output":   string,          OPTIONAL. Output file path. Default: "output.pdf"

  "page_size":    string,      OPTIONAL. "A4" (default), "Letter", or "Legal".

  "orientation":  string,      OPTIONAL. "portrait" (default) or "landscape".

  "theme": {                   OPTIONAL. Override brand colors. All values are
                               hex strings "#RRGGBB".
    "primary":  "#1A1A2E",     Header bar, headings, table header background.
    "accent":   "#E94560",     Divider lines, left border on highlight boxes,
                               footer rule, cover accent bar.
    "light":    "#F5F5F5",     Alternate table row background, highlight box bg.
    "text":     "#2D2D2D",     Body text color.
    "muted":    "#888888"      Captions, metadata labels, footer text.
  },

  "meta": {                    OPTIONAL. Key/value pairs shown on the cover page
                               below the title. Any string keys are accepted.
    "author":     string,
    "date"       | "fecha"
    | "datum":    string,      If omitted, today's date is used automatically.
                               Recognises "date", "fecha", or "datum".
    "version":    string,      Also shown in the page header (top-right).
    "department": string,
    ...                        Add any fields relevant to the document type.
  },

  "sections": [                REQUIRED. Array of section objects. Rendered in
    {                          order. Each section can mix any combination of
                               the elements below.

      "heading": string,       REQUIRED per section. Section title. Preceded by
                               a colored horizontal rule.

      "body": string,          OPTIONAL. One or more paragraphs of body text.
                               Rendered with justified alignment.
                               Supports inline XML markup: <b>, <i>, <br/>, etc.
                               Escape & as &amp;, < as &lt;, > as &gt;.

      "bullets": [string],     OPTIONAL. Unordered list. Each string is one
                               bullet item. Rendered with "•" prefix and left
                               indent. Supports inline markup per item.

      "highlight": string,     OPTIONAL. A call-out / pull-quote box. Renders
                               with a colored left border and light background.
                               Use for key insights, warnings, or summary stats.
                               Supports inline markup.

      "image": {               OPTIONAL. Embedded image.
        "path":     string,    REQUIRED. File path to the image.
        "width":    float,     OPTIONAL. Width in cm. Default: full text width.
        "height":   float,     OPTIONAL. Height in cm. Auto-aspect if omitted.
        "caption":  string     OPTIONAL. Centered italic caption below the image.
      },

      "code":      string,     OPTIONAL. Code block in monospace with gray
                               background. Escape XML as usual.
      "language":  string,     OPTIONAL. Shown as a label above the code block.
                               Only meaningful when "code" is present.

      "table": {               OPTIONAL. A data table.
        "headers": [string],   Column header labels. Rendered with white text
                               on dark (primary color) background.
        "rows": [[string]],    2D array of cell values. Each inner array is one
                               row. Cell count must match headers count.
        "col_widths": [float]  OPTIONAL. Column widths in cm. If omitted,
                               columns are distributed equally across the page.
                               Sum should not exceed ~17 cm for A4 with margins.
                               Example for 4 cols: [5.0, 4.0, 4.0, 4.0]
      },

      "note": string           OPTIONAL. A smaller, muted italic note below
                               the section content. Good for source citations,
                               disclaimers, or "as of" dates.
    }
  ]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT SYSTEM PROMPT (copy this into your agent's system instructions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  You are a document content agent. When asked to generate a report or document,
  respond ONLY with a valid JSON object following this schema exactly.
  Do not include any explanation, markdown fences, or text outside the JSON.

  Rules:
  1. "title" and "sections" are required. Every section must have "heading".
  2. Escape XML special characters in all text values:
       & → &amp;    < → &lt;    > → &gt;
  3. For "col_widths", provide values in cm as floats. Total must be ≤ 17.0.
  4. "bullets" is a flat array of strings, not nested objects.
  5. "rows" in a table is a 2D array: outer array = rows, inner = cells.
     Cell count per row must exactly match the number of headers.
   6. If no date key ("date", "fecha", or "datum") is provided in "meta", today's date will be used automatically as "date".
  7. Keep "highlight" to 1–3 sentences max. It's a call-out, not a paragraph.
  8. Do not put HTML or Markdown inside text values. Only use these XML tags:
       <b>text</b>   <i>text</i>   <br/>   <sub>text</sub>   <super>text</super>
  9. Output nothing but the JSON object.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KNOWN PITFALLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✗ Unicode sub/superscripts (₂ ³ ⁴) → black boxes. Use <sub>/<super> tags.
  ✗ Raw & in Paragraph text → XML parse error. Always escape as &amp;.
  ✗ col_widths sum > page text width → Table overflows margin silently.
  ✗ Empty string in table cell → Fine, but None/null → will crash. Use "".
  ✗ topMargin < header bar height → Body text rendered under the header bar.
  ✗ Mixing canvas drawing in story list → Crashes. Canvas calls belong ONLY
    in the onFirstPage / onLaterPages callbacks.
  ✗ saveState() without restoreState() in page callback → Corrupts subsequent
    page rendering. Always pair them.
  ✗ Setting fontSize in TableStyle FONT command without fontName → Ignored.
    Always provide both: ("FONT", ..., "Helvetica-Bold", 10)
  ✗ KeepTogether with a very tall block → If it's taller than one page,
    ReportLab ignores the keep and splits it anyway. Keep blocks short.
  ✗ Registering a TTF font but then referencing a variant name that was not
    registered → Silently falls back to Helvetica. Register each variant.
"""

import json
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfgen_canvas
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE SIZE RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────

PAGE_SIZES = {
    "A4":     A4,
    "Letter": LETTER,
    "Legal":  LEGAL,
}

def resolve_page_size(content: dict) -> tuple:
    """
    Resolve (width, height) in points from content["page_size"]
    and content["orientation"].

    page_size:  "A4" (default), "Letter", or "Legal".
    orientation: "portrait" (default) or "landscape".
    """
    raw   = content.get("page_size", "A4")
    pagesize = PAGE_SIZES.get(raw, A4)
    if content.get("orientation", "portrait") == "landscape":
        pagesize = (pagesize[1], pagesize[0])
    return pagesize

MARGIN = 2.0 * cm   # Left/right margin. Top/bottom set separately.

# ─────────────────────────────────────────────────────────────────────────────
# THEME BUILDER
# Accepts an optional "theme" dict from the content JSON.
# Falls back to professional dark-navy defaults for any missing key.
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_THEME = {
    "primary": "#1A1A2E",
    "accent":  "#E94560",
    "light":   "#F5F5F5",
    "text":    "#2D2D2D",
    "muted":   "#888888",
}

def build_theme(overrides: dict | None) -> dict:
    """
    Merge user theme overrides with defaults.
    Returns a dict of color NAME → reportlab Color object.
    """
    raw = {**DEFAULT_THEME, **(overrides or {})}
    return {k: colors.HexColor(v) for k, v in raw.items()}


# ─────────────────────────────────────────────────────────────────────────────
# ESCAPE HELPER
# Agents sometimes forget to escape XML special characters.
# This function sanitises incoming text before it reaches a Paragraph.
# ─────────────────────────────────────────────────────────────────────────────

def safe_xml(text: str) -> str:
    """
    Escape raw ampersands that are NOT already part of an XML entity.
    Does not escape < or > because agents legitimately use <b>, <i>, etc.
    Only & is truly dangerous — &foo; is valid XML but & alone is not.
    """
    # Replace & that is not followed by an entity pattern (word + semicolon)
    return re.sub(r'&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE TEMPLATE  (canvas-level chrome — header bar + footer)
# ─────────────────────────────────────────────────────────────────────────────

class PageChrome:
    """
    Handles header and footer drawing on every page.

    Why a class and not a plain function?
    Because we need to carry doc-level data (title, subtitle, theme) into
    the callback without using globals. The callback signature is fixed:
    fn(canvas, doc) — we can't add extra args. A class with __call__ is clean.

    The header is a filled rectangle spanning the full page width, drawn at
    canvas level so it sits behind/independent of the Platypus text flow.
    The footer is a thin accent line with page number and generation date.
    """

    HEADER_H = 1.8 * cm    # Height of the top header bar
    FOOTER_Y  = 1.5 * cm   # Y position of footer rule line

    def __init__(self, title: str, version: str, theme: dict):
        self.title   = title.upper()
        self.version = version
        self.C       = theme    # shorthand: C["primary"], C["accent"], etc.

    def __init__(self, title: str, version: str, theme: dict, margin: float):
        self.title   = title.upper()
        self.version = version
        self.C       = theme
        self.margin  = margin

    def __call__(self, c: pdfgen_canvas.Canvas, doc):
        """Called by SimpleDocTemplate.build() for every page."""
        c.saveState()
        self._header(c, doc)
        self._footer(c, doc)
        c.restoreState()

    def _header(self, c, doc):
        pw, ph = doc.pagesize
        c.setFillColor(self.C["primary"])
        c.rect(0, ph - self.HEADER_H, pw, self.HEADER_H,
               fill=True, stroke=False)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        bar_mid = ph - self.HEADER_H + (self.HEADER_H / 2)
        c.drawString(self.margin, bar_mid - 4, self.title)

        if self.version:
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#AAAACC"))
            c.drawRightString(pw - self.margin, bar_mid - 3, self.version)

    def _footer(self, c, doc):
        pw, _ = doc.pagesize
        c.setStrokeColor(self.C["accent"])
        c.setLineWidth(1.5)
        c.line(self.margin, self.FOOTER_Y, pw - self.margin, self.FOOTER_Y)

        c.setFont("Helvetica", 8)

        c.setFillColor(self.C["muted"])
        c.drawCentredString(pw / 2, self.FOOTER_Y - 10,
                            f"— {doc.page} —")

        date_str = datetime.now().strftime("%d %b %Y")
        c.drawRightString(pw - self.margin, self.FOOTER_Y - 10, date_str)


# ─────────────────────────────────────────────────────────────────────────────
# STYLE SHEET
# Build a complete, named type system. Every text element in the document
# references one of these styles by the dict key.
#
# Why not use getSampleStyleSheet() directly?
# Because its default styles (Normal, Heading1, etc.) have arbitrary sizes
# and colors. Defining our own gives full predictability and easy theming.
# ─────────────────────────────────────────────────────────────────────────────

def build_styles(C: dict) -> dict:
    """
    Build the full style sheet, themed with the resolved color dict C.

    Naming convention:
      cover_*     — Cover page elements (large, display-scale)
      section_*   — Section-level heading
      body_*      — Body text variants
      table_*     — Table cell styles
      meta_*      — Metadata / caption / label text
    """
    return {

        # ── COVER PAGE ────────────────────────────────────────────────────
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName  = "Helvetica-Bold",
            fontSize  = 30,
            leading   = 36,          # line height = 36pt
            textColor = C["primary"],
            spaceAfter= 6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName  = "Helvetica",
            fontSize  = 13,
            leading   = 18,
            textColor = C["muted"],
            spaceAfter= 20,
        ),

        # ── SECTION HEADINGS ──────────────────────────────────────────────
        "section_heading": ParagraphStyle(
            "section_heading",
            fontName    = "Helvetica-Bold",
            fontSize    = 13,
            leading     = 17,
            textColor   = C["primary"],
            spaceBefore = 6,
            spaceAfter  = 4,
        ),

        # ── BODY TEXT ─────────────────────────────────────────────────────
        "body": ParagraphStyle(
            "body",
            fontName  = "Helvetica",
            fontSize  = 10,
            leading   = 15,          # 1.5× fontSize — comfortable reading
            textColor = C["text"],
            spaceAfter= 8,
            alignment = TA_JUSTIFY,  # Justified body text = professional look
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName    = "Helvetica",
            fontSize    = 10,
            leading     = 14,
            textColor   = C["text"],
            leftIndent  = 14,        # indent from left margin
            spaceAfter  = 3,
        ),
        "note": ParagraphStyle(
            "note",
            fontName  = "Helvetica-Oblique",
            fontSize  = 8,
            leading   = 11,
            textColor = C["muted"],
            spaceAfter= 6,
        ),

        # ── HIGHLIGHT BOX ─────────────────────────────────────────────────
        "highlight": ParagraphStyle(
            "highlight",
            fontName  = "Helvetica-Bold",
            fontSize  = 10,
            leading   = 15,
            textColor = C["primary"],
            leftIndent= 10,
        ),

        # ── TABLE CELLS ───────────────────────────────────────────────────
        "table_header": ParagraphStyle(
            "table_header",
            fontName  = "Helvetica-Bold",
            fontSize  = 9,
            leading   = 12,
            textColor = colors.white,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName  = "Helvetica",
            fontSize  = 9,
            leading   = 12,
            textColor = C["text"],
        ),

        # ── COVER PAGE METADATA ───────────────────────────────────────────
        "meta_key": ParagraphStyle(
            "meta_key",
            fontName  = "Helvetica-Bold",
            fontSize  = 9,
            leading   = 13,
            textColor = C["muted"],
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName  = "Helvetica",
            fontSize  = 9,
            leading   = 13,
            textColor = C["text"],
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT BUILDERS
# Each function returns a list of Flowables to be appended into the story.
# This pattern makes the main builder clean and declarative.
# ─────────────────────────────────────────────────────────────────────────────

def make_cover(title: str, subtitle: str, meta: dict,
               S: dict, C: dict, text_width: float) -> list:
    """
    Build the cover page flowable list.

    Layout:
      [4 cm spacer]
      [accent bar | title block]
      [metadata table]
      [PageBreak]

    The accent bar + title are placed side-by-side using a 2-column Table
    rather than canvas drawing, so they stay in the Platypus flow and are
    not hard-coded to pixel positions.
    """
    elems = [Spacer(1, 3.5 * cm)]

    # Accent bar (left column) + title block (right column)
    accent_bar = Table(
        [[" "]],
        colWidths=[0.8 * cm],
        rowHeights=[4.5 * cm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C["accent"]),
        ]),
    )
    title_block = [
        Paragraph(safe_xml(title), S["cover_title"]),
    ]
    if subtitle:
        title_block.append(Paragraph(safe_xml(subtitle), S["cover_subtitle"]))

    layout = Table(
        [[accent_bar, title_block]],
        colWidths=[1.2 * cm, text_width - 1.2 * cm],
        style=TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (1, 0), (1, 0),   14),
            ("TOPPADDING",   (0, 0), (-1, -1),  0),
            ("BOTTOMPADDING",(0, 0), (-1, -1),  0),
        ]),
    )
    elems.append(layout)
    elems.append(Spacer(1, 12))
    elems.append(HRFlowable(width="100%", thickness=0.75,
                            color=C["muted"], spaceAfter=10))

    # Metadata key/value table
    if meta:
        rows = [
            [Paragraph(k.title() + ":", S["meta_key"]),
             Paragraph(safe_xml(str(v)), S["meta_value"])]
            for k, v in meta.items()
        ]
        meta_table = Table(
            rows,
            colWidths=[4 * cm, text_width - 4 * cm],
            style=TableStyle([
                ("TOPPADDING",    (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ]),
        )
        elems.append(meta_table)

    elems.append(PageBreak())
    return elems


def make_section_header(heading: str, S: dict, C: dict) -> list:
    """
    Render a section heading with a two-tone horizontal rule above it.
    Returns [HRFlowable, Paragraph] — these two are always KeepTogether'd
    with the first body element so headings never orphan at a page bottom.
    """
    return [
        HRFlowable(
            width="100%", thickness=2,
            color=C["accent"], spaceAfter=4, spaceBefore=10,
        ),
        Paragraph(safe_xml(heading), S["section_heading"]),
    ]


def make_body(text: str, S: dict) -> list:
    """Single body paragraph. Text may contain inline XML markup."""
    return [Paragraph(safe_xml(text), S["body"])]


def make_bullets(items: list[str], S: dict) -> list:
    """
    Bulleted list. Each item gets a "•" prefix and left indent.
    Using explicit bullet character in the text rather than ParagraphStyle
    bulletText because bulletText requires careful bulletIndent tuning.
    """
    elems = []
    for item in items:
        elems.append(Paragraph(f"&bull; {safe_xml(item)}", S["bullet"]))
    elems.append(Spacer(1, 4))
    return elems


def make_highlight(text: str, S: dict, C: dict, text_width: float) -> list:
    """
    Call-out box: light background, colored left border, bold text.
    Implemented as a single-cell Table so we can control the left border
    independently — ParagraphStyle doesn't support per-side borders.
    """
    inner = Paragraph(safe_xml(text), S["highlight"])
    box = Table(
        [[inner]],
        colWidths=[text_width],
        style=TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C["light"]),
            ("LEFTPADDING",  (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
            # Left accent border: LINEBEFORE draws on the left edge
            ("LINEBEFORE",   (0, 0), (0, -1), 4, C["accent"]),
        ]),
    )
    return [box, Spacer(1, 8)]


def make_image(img: dict, S: dict, text_width: float) -> list:
    """
    Embed an image. The image dict can contain:
      path:    str  (required) — file path
      width:   float (optional, cm) — default text_width
      height:  float (optional, cm) — auto aspect if omitted
      caption: str   (optional) — centered italic caption below
    """
    path = img.get("path", "")
    if not path:
        return []
    w_cm = img.get("width")
    w_pt = w_cm * cm if w_cm else text_width
    h_cm = img.get("height")
    h_pt = h_cm * cm if h_cm else None
    try:
        rl_img = RLImage(path, width=w_pt, height=h_pt) if h_pt else RLImage(path, width=w_pt)
    except Exception:
        return [Paragraph(f"<i>[Image not found: {safe_xml(path)}]</i>", S["note"])]
    elems = [rl_img, Spacer(1, 2)]
    caption = img.get("caption")
    if caption:
        cap_style = ParagraphStyle(
            "image_caption",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#888888"),
            alignment=TA_CENTER,
            spaceAfter=8,
        )
        elems.append(Paragraph(safe_xml(caption), cap_style))
    elems.append(Spacer(1, 4))
    return elems


def make_table(headers: list[str], rows: list[list[str]],
               col_widths_cm: list[float] | None,
               S: dict, C: dict, text_width: float) -> list:
    """
    Data table with a styled header row and alternating row backgrounds.

    col_widths_cm: list of floats in CENTIMETRES. If None, columns are
    distributed equally. If provided, values are converted to points.
    Total should not exceed TEXT_WIDTH / cm ≈ 17 cm for A4.

    repeatRows=1 means the header row repeats at the top of each page
    if the table spans multiple pages — critical for long tables.
    """
    # Convert header strings to styled Paragraphs
    header_row = [Paragraph(safe_xml(h), S["table_header"]) for h in headers]

    # Convert cell values to styled Paragraphs
    # Empty/None cells are rendered as empty string to avoid crashes
    data_rows = [
        [Paragraph(safe_xml(str(cell)) if cell is not None else "", S["table_cell"])
         for cell in row]
        for row in rows
    ]

    all_data = [header_row] + data_rows

    # Resolve column widths
    if col_widths_cm:
        col_w = [w * cm for w in col_widths_cm]
    else:
        n = len(headers)
        col_w = [text_width / n] * n

    t = Table(
        all_data,
        colWidths=col_w,
        repeatRows=1,    # ← repeat header row on every page if table is long
        style=TableStyle([
            # Header row styling
            ("BACKGROUND",    (0, 0), (-1, 0),  C["primary"]),
            ("LINEBELOW",     (0, 0), (-1, 0),  2, C["accent"]),
            # Alternating row backgrounds (applied to data rows only)
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C["light"]]),
            # Grid
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            # Padding
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]),
    )
    return [t, Spacer(1, 8)]


def make_code(code_text: str, language: str, C: dict, text_width: float) -> list:
    """
    Code block with monospace font, light gray background, and optional
    language label in the top-right corner.
    """
    code_style = ParagraphStyle(
        "code_block",
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=C["text"],
        backColor=C["light"],
    )
    inner = Paragraph(safe_xml(code_text), code_style)
    rows = []
    if language:
        lang_style = ParagraphStyle(
            "code_lang",
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=9,
            textColor=C["muted"],
            alignment=TA_RIGHT,
        )
        rows.append([Paragraph(safe_xml(language), lang_style)])
    rows.append([inner])

    box = Table(
        rows,
        colWidths=[text_width],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C["light"]),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ] + ([
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#DDDDDD")),
        ] if language else [])),
    )
    return [box, Spacer(1, 8)]


def make_note(text: str, S: dict) -> list:
    """Small italic note / source citation below a section."""
    return [Paragraph(safe_xml(text), S["note"]), Spacer(1, 4)]


# ─────────────────────────────────────────────────────────────────────────────
# SECTION ASSEMBLER
# Converts one section dict → list of Flowables.
# ─────────────────────────────────────────────────────────────────────────────

def assemble_section(section: dict, S: dict, C: dict, text_width: float) -> list:
    """
    Build all flowables for one section from the content JSON.

    KeepTogether strategy:
    We wrap the section header + first body element together so the heading
    is never left alone at the bottom of a page (orphan heading).
    The rest of the section content flows freely.
    """
    heading = section.get("heading", "")
    body    = section.get("body", "")
    bullets = section.get("bullets", [])
    hl      = section.get("highlight", "")
    img     = section.get("image")
    code    = section.get("code")
    lang    = section.get("language", "")
    tbl     = section.get("table")
    note    = section.get("note", "")

    header_elems = make_section_header(heading, S, C)

    # Collect everything that follows the heading
    body_elems = []
    if body:
        body_elems += make_body(body, S)
    if bullets:
        body_elems += make_bullets(bullets, S)
    if hl:
        body_elems += make_highlight(hl, S, C, text_width)
    if img:
        body_elems += make_image(img, S, text_width)
    if code:
        body_elems += make_code(code, lang, C, text_width)
    if tbl:
        body_elems += make_table(
            tbl.get("headers", []),
            tbl.get("rows", []),
            tbl.get("col_widths"),
            S, C, text_width,
        )
    if note:
        body_elems += make_note(note, S)

    if not body_elems:
        return header_elems

    # KeepTogether: heading + first content element stay on the same page
    anchored = KeepTogether(header_elems + [body_elems[0]])
    return [anchored] + body_elems[1:]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build_pdf(content: dict, output_path: str | None = None) -> str:
    """
    Build a complete professional PDF from a content dict.

    Args:
        content:     Dict matching the documented schema above.
        output_path: Override the output file path. If None, uses
                     content["output"] or defaults to "output.pdf".

    Returns:
        The absolute path to the generated PDF file.
    """

    # ── Resolve output path ──────────────────────────────────────────────
    out = output_path or content.get("output", "output.pdf")

    # ── Resolve theme ────────────────────────────────────────────────────
    C = build_theme(content.get("theme"))

    # ── Resolve meta ─────────────────────────────────────────────────────
    meta = dict(content.get("meta", {}))
    date_keys = {"date", "fecha", "datum"}
    if not date_keys.intersection(k.lower() for k in meta):
        meta["date"] = datetime.now().strftime("%B %d, %Y")

    # ── Resolve page size ────────────────────────────────────────────────
    page_w, page_h = resolve_page_size(content)
    text_width = page_w - 2 * MARGIN

    # ── Build style sheet ────────────────────────────────────────────────
    S = build_styles(C)

    # ── Page chrome (header/footer) ──────────────────────────────────────
    chrome = PageChrome(
        title   = content.get("title", "Document"),
        version = meta.get("version", ""),
        theme   = C,
        margin  = MARGIN,
    )

    # ── Document template ────────────────────────────────────────────────
    # topMargin must be > PageChrome.HEADER_H (1.8 cm) so body doesn't
    # render behind the header bar. bottomMargin must clear the footer.
    doc = SimpleDocTemplate(
        out,
        pagesize     = (page_w, page_h),
        leftMargin   = MARGIN,
        rightMargin  = MARGIN,
        topMargin    = 2.2 * cm,
        bottomMargin = 2.0 * cm,
    )

    # ── Build story ──────────────────────────────────────────────────────
    story = []

    # Cover page (always present)
    story += make_cover(
        content.get("title", "Untitled"),
        content.get("subtitle", ""),
        meta,
        S, C, text_width,
    )

    # Sections
    for section in content.get("sections", []):
        story += assemble_section(section, S, C, text_width)

    # ── Render ───────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=chrome, onLaterPages=chrome)

    return str(Path(out).resolve())


# ─────────────────────────────────────────────────────────────────────────────
# CLI INTERFACE
# Accepts either a raw JSON string or a path to a JSON file.
# Used by agent tool wrappers to call this as a subprocess.
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_engine.py '<json_string>'")
        print("       python pdf_engine.py path/to/content.json")
        sys.exit(1)

    arg = sys.argv[1]

    # Determine if arg is a file path or raw JSON
    p = Path(arg)
    if p.exists() and p.suffix == ".json":
        with open(p, "r", encoding="utf-8") as f:
            content = json.load(f)
    else:
        # Strip markdown fences if an agent accidentally wraps the JSON
        clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", arg.strip())
        content = json.loads(clean)

    # Allow output path override as second CLI argument
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = build_pdf(content, output_path)
    print(f"OK:{result}")   # parseable output for agent tool wrappers


if __name__ == "__main__":
    main()
