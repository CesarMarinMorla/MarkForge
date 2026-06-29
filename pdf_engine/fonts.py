"""
Font registration for the Agent PDF Engine.
Handles TTF registration, system font detection, and fallback chains.
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


DEFAULT_FONTS = {
    "sans":       ("Helvetica",        "Helvetica-Bold",  "Helvetica-Oblique",  "Helvetica-BoldOblique"),
    "mono":       ("Courier",          "Courier-Bold",    "Courier-Oblique",    "Courier-BoldOblique"),
    "serif":      ("Times-Roman",      "Times-Bold",      "Times-Italic",       "Times-BoldItalic"),
}


def register_user_fonts(fonts_config: dict | None) -> dict:
    """
    Register TTF fonts from the content's "fonts" block and return a
    dict mapping each role -> (regular, bold, italic, bold_italic) font names.

    If fonts_config is None or empty, returns DEFAULT_FONTS unchanged.
    """
    resolved = dict(DEFAULT_FONTS)

    if not fonts_config:
        return resolved

    for role in ("sans", "mono", "serif"):
        cfg = fonts_config.get(role)
        if not cfg:
            continue

        reg_path = cfg.get("regular", "")
        bold_path = cfg.get("bold", "")
        italic_path = cfg.get("italic", "")
        bi_path = cfg.get("bold_italic", "")

        base_name = f"Custom{role.capitalize()}"
        reg_name = base_name
        bold_name = f"{base_name}-Bold"
        italic_name = f"{base_name}-Italic"
        bi_name = f"{base_name}-BoldItalic"

        if reg_path:
            try:
                pdfmetrics.registerFont(TTFont(reg_name, reg_path))
            except Exception:
                reg_name = resolved[role][0]

        if bold_path and reg_name.startswith("Custom"):
            try:
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            except Exception:
                bold_name = resolved[role][1]
        elif not bold_path:
            bold_name = resolved[role][1]

        if italic_path and reg_name.startswith("Custom"):
            try:
                pdfmetrics.registerFont(TTFont(italic_name, italic_path))
            except Exception:
                italic_name = resolved[role][2]
        elif not italic_path:
            italic_name = resolved[role][2]

        if bi_path and reg_name.startswith("Custom"):
            try:
                pdfmetrics.registerFont(TTFont(bi_name, bi_path))
            except Exception:
                bi_name = resolved[role][3]
        elif not bi_path:
            bi_name = resolved[role][3]

        resolved[role] = (reg_name, bold_name, italic_name, bi_name)

    return resolved
