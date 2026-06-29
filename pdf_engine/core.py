"""
Core entry point for the Agent PDF Engine.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Spacer,
    SimpleDocTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents

from pdf_engine.chrome import PageChrome
from pdf_engine.components import assemble_section, make_cover
from pdf_engine.fonts import register_user_fonts
from pdf_engine.schema import validate_content
from pdf_engine.styles import build_styles
from pdf_engine.theme import build_theme


PAGE_SIZES = {
    "A4":     A4,
    "Letter": LETTER,
    "Legal":  LEGAL,
}

MARGIN = 2.0 * cm


def resolve_page_size(content: dict) -> tuple:
    """Resolve (width, height) in points from content page_size and orientation."""
    raw   = content.get("page_size", "A4")
    pagesize = PAGE_SIZES.get(raw, A4)
    if content.get("orientation", "portrait") == "landscape":
        pagesize = (pagesize[1], pagesize[0])
    return pagesize


def build_pdf(content: dict, output_path: str | None = None) -> str:
    """
    Build a complete professional PDF from a content dict.

    Flow:
      0. validate_content(content) -> raises ValueError with all errors
      1. content.get("theme")  -> build_theme()    -> C (color dict)
      2. content.get("fonts")  -> register_user_fonts() -> F (font name dict)
      3. C + F                 -> build_styles()     -> S (ParagraphStyle dict)
      4. story = make_cover() + [toc] + assemble_section() per section
      5. doc.multiBuild(story, onFirstPage=chrome, onLaterPages=chrome)

    Returns the absolute path to the generated PDF file.
    """
    # ── Validate schema ──────────────────────────────────────────────────
    errs = validate_content(content)
    if errs:
        raise ValueError(
            "Content validation failed:\n  - " + "\n  - ".join(errs)
        )

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

    # ── Register custom fonts ────────────────────────────────────────────
    F = register_user_fonts(content.get("fonts"))

    # ── Build style sheet ────────────────────────────────────────────────
    S = build_styles(C, F)

    # ── Page chrome (header/footer) ──────────────────────────────────────
    chrome = PageChrome(
        title           = content.get("title", "Document"),
        version         = meta.get("version", ""),
        theme           = C,
        margin          = MARGIN,
        show_footer_date = content.get("show_footer_date", True),
        watermark       = content.get("watermark", ""),
        hf_config       = content.get("header_footer"),
        font_dict       = F,
    )

    # ── Document template ────────────────────────────────────────────────
    hf_cfg = content.get("header_footer", {})
    header_shown = hf_cfg.get("header", {}).get("show", True)
    top_margin = 1.0 * cm if not header_shown else 2.2 * cm
    doc = SimpleDocTemplate(
        out,
        pagesize     = (page_w, page_h),
        leftMargin   = MARGIN,
        rightMargin  = MARGIN,
        topMargin    = top_margin,
        bottomMargin = 2.0 * cm,
    )

    # ── Build story ──────────────────────────────────────────────────────
    show_toc = content.get("show_toc", False)
    show_cover = content.get("show_cover", True)
    story = []

    if show_cover:
        story += make_cover(
            content.get("title", "Untitled"),
            content.get("subtitle", ""),
            meta,
            S, C, text_width,
        )

    if show_toc:
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                "toc_level_1",
                fontName="Helvetica",
                fontSize=10,
                leading=16,
                textColor=C["text"],
                leftIndent=0,
            ),
        ]
        story.append(toc)
        story.append(Spacer(1, 12))

    mono_font = F["mono"][0]
    for section in content.get("sections", []):
        story += assemble_section(section, S, C, text_width, show_toc, mono_font)

    doc.multiBuild(story, onFirstPage=chrome, onLaterPages=chrome)

    return str(Path(out).resolve())


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m pdf_engine '<json_string>'")
        print("       python -m pdf_engine path/to/content.json")
        sys.exit(1)

    arg = sys.argv[1]

    p = Path(arg)
    if p.exists() and p.suffix == ".json":
        with open(p, "r", encoding="utf-8") as f:
            content = json.load(f)
    else:
        clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", arg.strip())
        content = json.loads(clean)

    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    result = build_pdf(content, output_path)
    print(f"OK:{result}")
