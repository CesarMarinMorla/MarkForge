"""
Component builders for MarkForge.
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
from reportlab.platypus.tableofcontents import SimpleIndex

# ── Inline code rounded background ──────────────────────────────────────────
# Monkey-patch ReportLab's _do_post_text to use roundRect instead of rect
# for inline fragment backColors (code spans rendered with rounded corners).
import reportlab.platypus.paragraph as _rl_para

_original_do_post_text = _rl_para._do_post_text


def _patched_do_post_text(tx):
    xs = tx.XtraState
    y0 = xs.cur_y
    f = xs.f
    leading = xs.style.leading
    autoLeading = xs.autoLeading
    fontSize = f.fontSize
    if autoLeading == 'max':
        leading = max(leading, 1.2 * fontSize)
    elif autoLeading == 'min':
        leading = 1.2 * fontSize

    if xs.backColors:
        yl = y0 + fontSize
        ydesc = yl - leading
        pad = 1.5
        vpad = 0.5
        for x1, x2, c in xs.backColors:
            tx._canvas.setFillColor(c)
            tx._canvas.roundRect(x1 - pad, ydesc + vpad, x2 - x1 + 2 * pad,
                                 leading - 2 * vpad, radius=2, stroke=0, fill=1)
        xs.backColors = []
        xs.backColor = None

    for (((n, link), x1), lo, hi), x2 in sorted(xs.links.values()):
        _rl_para._doLink(tx, link, (x1, y0 + lo, x2, y0 + hi))
    xs.links = {}

    if xs.us_lines:
        dw = tx._defaultLineWidth
        values = dict(L=fontSize)
        for (((n, k, c, w, o, r, m, g), fs, tc, x1), fsmax), x2 in \
                sorted(xs.us_lines.values()):
            underline = k == 'underline'
            values['f'] = fs
            values['F'] = fsmax
            lw = _rl_para._usConv(w, values, default=tx._defaultLineWidth)
            lg = _rl_para._usConv(g, values, default=1)
            dy = lg + lw
            if not underline:
                dy = -dy
            y = y0 + r + _rl_para._usConv(
                o if o != '' else ('-0.125*L' if underline else '0.25*L'),
                values,
            )
            if not c:
                c = tc
            while m > 0:
                tx._do_line(x1, y, x2, y, lw, c)
                y -= dy
                m -= 1
        xs.us_lines = {}

    xs.cur_y -= leading


_rl_para._do_post_text = _patched_do_post_text


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
        p._tocInfo = (0, heading)
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


def make_bullets(items: list[str], S: dict,
                 levels: list[int] | None = None) -> list:
    """Bulleted list with bullets, optional nesting levels (0=top)."""
    elems = []
    for idx, item in enumerate(items):
        level = levels[idx] if levels else 0
        indent = level * 20
        style = ParagraphStyle(
            "nested_bullet",
            parent=S["bullet"],
            leftIndent=S["bullet"].leftIndent + indent,
        )
        elems.append(Paragraph(f"&bull; {safe_xml(item)}", style))
    elems.append(Spacer(1, 4))
    return elems


def make_task_list(items: list[str], checked: list[bool], S: dict) -> list:
    """Task list with checkbox markers."""
    elems = []
    for item, chk in zip(items, checked):
        char = "&#x2611;" if chk else "&#x2610;"
        elems.append(Paragraph(f'{char} {safe_xml(item)}', S["bullet"]))
    elems.append(Spacer(1, 4))
    return elems


def make_ordered_list(items: list[str], S: dict,
                      levels: list[int] | None = None) -> list:
    """Ordered list with 1. 2. 3. prefix, optional nesting."""
    elems = []
    for idx, item in enumerate(items):
        level = levels[idx] if levels else 0
        indent = level * 20
        style = ParagraphStyle(
            "nested_ordered",
            parent=S["bullet"],
            leftIndent=S["bullet"].leftIndent + indent,
        )
        elems.append(Paragraph(f"<b>{idx + 1}.</b>&nbsp; {safe_xml(item)}", style))
    elems.append(Spacer(1, 4))
    return elems


def make_definition_list(terms: list[str], defs: list[str], S: dict) -> list:
    """Definition list: term (bold) + indented definitions."""
    elems = []
    for term in terms:
        elems.append(Paragraph(f"<b>{safe_xml(term)}</b>", S["body"]))
    for d in defs:
        style = ParagraphStyle(
            "definition",
            parent=S["body"],
            leftIndent=S["body"].leftIndent + 20,
        )
        elems.append(Paragraph(safe_xml(d), style))
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
               S: dict, C: dict, text_width: float,
               caption: str | None = None,
               table_style: dict | None = None) -> list:
    """Data table with styled header and alternating row backgrounds.

    ``table_style`` keys (all optional):
        header_bg  — header background color (default C["primary"])
        stripe     — enable alternating row colors (default True)
        stripe_a   — first stripe color (default colors.white)
        stripe_b   — second stripe color (default C["light"])
        grid       — enable grid lines (default True)
        grid_color — grid line color (default "#DDDDDD")
    """
    ts = table_style or {}

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

    tbl_style = [
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]

    hdr_bg = ts.get("header_bg", C["primary"])
    tbl_style.append(("BACKGROUND", (0, 0), (-1, 0),
                      colors.HexColor(hdr_bg) if isinstance(hdr_bg, str) else hdr_bg))
    tbl_style.append(("LINEBELOW", (0, 0), (-1, 0), 2, C["accent"]))

    if ts.get("stripe", True):
        stripe_a = ts.get("stripe_a", colors.white)
        stripe_b = ts.get("stripe_b", C["light"])
        tbl_style.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [stripe_a, stripe_b]))

    if ts.get("grid", True):
        gc = ts.get("grid_color", "#DDDDDD")
        tbl_style.append(("GRID", (0, 0), (-1, -1), 0.5,
                          colors.HexColor(gc) if isinstance(gc, str) else gc))

    t = Table(all_data, colWidths=col_w, repeatRows=1,
              style=TableStyle(tbl_style))
    elems = []
    if caption:
        elems.append(Paragraph(safe_xml(caption), S["image_caption"]))
    elems += [t, Spacer(1, 8)]
    return elems


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


SUB_HEADING_STYLES = {
    3: "sub_heading",
    4: "sub_sub_heading",
    5: "sub_sub_sub_heading",
    6: "sub_sub_sub_sub_heading",
}


def make_sub_heading(level: int, text: str, S: dict) -> list:
    """Sub-heading paragraph with style matching heading level."""
    style_key = SUB_HEADING_STYLES.get(level, "sub_sub_sub_sub_heading")
    return [Paragraph(safe_xml(text), S[style_key])]


def make_note(text: str, S: dict) -> list:
    """Small italic note / source citation."""
    return [Paragraph(safe_xml(text), S["note"]), Spacer(1, 4)]


def make_index(F: dict, C: dict, text_width: float) -> list:
    """Back-of-book index with alphabetical headers and dotted leaders."""
    idx = SimpleIndex(
        style=ParagraphStyle(
            "index_entry",
            fontName=F["sans"][0],
            fontSize=9,
            leading=14,
            textColor=C["text"],
        ),
        dot=" . ",
        headers=True,
        format="123",
    )
    return [Spacer(1, 20), idx]


def _render_blocks(blocks: list[dict], S: dict, C: dict, text_width: float,
                   mono_font: str) -> list:
    """Render an ordered list of content blocks to flowables."""
    elems = []
    for block in blocks:
        t = block.get("type")
        if t == "paragraph":
            elems += make_body(block.get("content", ""), S)
        elif t == "sub_heading":
            elems += make_sub_heading(block.get("level", 3),
                                      block.get("content", ""), S)
        elif t == "bullet":
            elems += make_bullets(block.get("items", []), S,
                                  levels=block.get("levels"))
        elif t == "task_list":
            elems += make_task_list(block.get("items", []), block.get("checked", []), S)
        elif t == "ordered":
            elems += make_ordered_list(block.get("items", []), S,
                                       levels=block.get("levels"))
        elif t == "definition":
            elems += make_definition_list(
                block.get("terms", []), block.get("defs", []), S)
        elif t == "highlight":
            elems += make_highlight(block.get("content", ""), S, C, text_width)
        elif t == "code":
            elems += make_code(block.get("content", ""),
                               block.get("language", ""),
                               C, text_width, mono_font)
        elif t == "table":
            elems += make_table(
                block.get("headers", []),
                block.get("rows", []),
                block.get("col_widths"),
                S, C, text_width,
                caption=block.get("caption"),
            )
        elif t == "image":
            elems += make_image(block, S, text_width)
        elif t == "note":
            elems += make_note(block.get("content", ""), S)
    return elems


def assemble_section(section: dict, S: dict, C: dict, text_width: float,
                     toc: bool = False, mono_font: str = "Courier") -> list:
    """Build all flowables for one section from the content JSON."""
    heading    = section.get("heading", "")
    pg_break   = section.get("page_break", False)
    blocks     = section.get("blocks")

    header_elems = make_section_header(heading, S, C, toc)
    if pg_break:
        header_elems.insert(0, PageBreak())

    if blocks:
        body_elems = _render_blocks(blocks, S, C, text_width, mono_font)
    else:
        # Backward-compat: old field-based section format
        body       = section.get("body", "")
        bullets    = section.get("bullets", [])
        ordered    = section.get("ordered_list", [])
        hl         = section.get("highlight", "")
        img        = section.get("image")
        code       = section.get("code")
        lang       = section.get("language", "")
        tbl        = section.get("table")
        note       = section.get("note", "")

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
                caption=tbl.get("caption"),
            )
        if note:
            body_elems += make_note(note, S)

    if not body_elems:
        return header_elems

    anchored = KeepTogether(header_elems + [body_elems[0]])
    # Propagate _tocInfo from heading Paragraph to KeepTogether wrapper
    # so afterFlowable can notify the TOC.
    for elem in header_elems:
        if hasattr(elem, '_tocInfo'):
            anchored._tocInfo = elem._tocInfo
            break
    return [anchored] + body_elems[1:]
