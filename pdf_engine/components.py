"""
Component builders for the Agent PDF Engine.
Each function returns a list of Flowables to be appended into the story.
"""

import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


def safe_xml(text: str) -> str:
    """Escape raw ampersands not already part of an XML entity."""
    return re.sub(r'&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)


def make_cover(title: str, subtitle: str, meta: dict,
               S: dict, C: dict, text_width: float) -> list:
    """Build the cover page flowable list."""
    elems = [Spacer(1, 3.5 * cm)]

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


def make_section_header(heading: str, S: dict, C: dict, toc: bool = False) -> list:
    """Render a section heading with a two-tone horizontal rule above it."""
    p = Paragraph(safe_xml(heading), S["section_heading"])
    if toc:
        p._tocInfo = (1, heading)
    return [
        HRFlowable(
            width="100%", thickness=2,
            color=C["accent"], spaceAfter=4, spaceBefore=10,
        ),
        p,
    ]


def make_body(text: str, S: dict) -> list:
    """Single body paragraph with inline XML markup."""
    return [Paragraph(safe_xml(text), S["body"])]


def make_bullets(items: list[str], S: dict) -> list:
    """Bulleted list with bullet prefix and left indent."""
    elems = []
    for item in items:
        elems.append(Paragraph(f"&bull; {safe_xml(item)}", S["bullet"]))
    elems.append(Spacer(1, 4))
    return elems


def make_ordered_list(items: list[str], S: dict) -> list:
    """Ordered list with 1. 2. 3. prefix."""
    elems = []
    for i, item in enumerate(items, start=1):
        elems.append(Paragraph(f"<b>{i}.</b>&nbsp; {safe_xml(item)}", S["bullet"]))
    elems.append(Spacer(1, 4))
    return elems


def make_highlight(text: str, S: dict, C: dict, text_width: float) -> list:
    """Call-out box with light background and colored left border."""
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
            ("LINEBEFORE",   (0, 0), (0, -1), 4, C["accent"]),
        ]),
    )
    return [box, Spacer(1, 8)]


def make_image(img: dict, S: dict, text_width: float) -> list:
    """Embed an image with optional caption."""
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
        elems.append(Paragraph(safe_xml(caption), S["image_caption"]))
    elems.append(Spacer(1, 4))
    return elems


def make_table(headers: list[str], rows: list[list[str]],
               col_widths_cm: list[float] | None,
               S: dict, C: dict, text_width: float) -> list:
    """Data table with styled header and alternating row backgrounds."""

    def _cell_text(cell):
        if cell is None:
            return ""
        if not isinstance(cell, str):
            return str(cell)
        return cell

    header_row = [Paragraph(safe_xml(h), S["table_header"]) for h in headers]

    data_rows = [
        [Paragraph(safe_xml(_cell_text(cell)), S["table_cell"])
         for cell in row]
        for row in rows
    ]

    all_data = [header_row] + data_rows

    if col_widths_cm:
        col_w = [w * cm for w in col_widths_cm]
    else:
        n = len(headers)
        lens = [max(len(h), 1) for h in headers]
        total_len = sum(lens)
        col_w = [text_width * (l / total_len) for l in lens]

    t = Table(
        all_data,
        colWidths=col_w,
        repeatRows=1,
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  C["primary"]),
            ("LINEBELOW",     (0, 0), (-1, 0),  2, C["accent"]),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C["light"]]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]),
    )
    return [t, Spacer(1, 8)]


def make_code(code_text: str, language: str, C: dict, text_width: float,
              mono_font: str = "Courier") -> list:
    """Code block with monospace font and gray background."""
    code_style = ParagraphStyle(
        "code_block",
        fontName=mono_font,
        fontSize=8,
        leading=11,
        textColor=C["text"],
        backColor=C["light"],
    )
    inner = Preformatted(code_text, code_style)

    box = Table(
        [[inner]],
        colWidths=[text_width],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C["light"]),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]),
    )
    return [box, Spacer(1, 8)]


def make_note(text: str, S: dict) -> list:
    """Small italic note / source citation."""
    return [Paragraph(safe_xml(text), S["note"]), Spacer(1, 4)]


def assemble_section(section: dict, S: dict, C: dict, text_width: float,
                     toc: bool = False, mono_font: str = "Courier") -> list:
    """Build all flowables for one section from the content JSON."""
    heading    = section.get("heading", "")
    body       = section.get("body", "")
    bullets    = section.get("bullets", [])
    ordered    = section.get("ordered_list", [])
    hl         = section.get("highlight", "")
    img        = section.get("image")
    code       = section.get("code")
    lang       = section.get("language", "")
    tbl        = section.get("table")
    note       = section.get("note", "")
    pg_break   = section.get("page_break", False)

    header_elems = make_section_header(heading, S, C, toc)
    if pg_break:
        header_elems.insert(0, PageBreak())

    body_elems = []
    if body:
        body_elems += make_body(body, S)
    if bullets:
        body_elems += make_bullets(bullets, S)
    if ordered:
        body_elems += make_ordered_list(ordered, S)
    if hl:
        body_elems += make_highlight(hl, S, C, text_width)
    if img:
        body_elems += make_image(img, S, text_width)
    if code:
        body_elems += make_code(code, lang, C, text_width, mono_font)
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

    anchored = KeepTogether(header_elems + [body_elems[0]])
    return [anchored] + body_elems[1:]
