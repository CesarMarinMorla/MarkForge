"""
Style sheet builder for MarkForge.
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle

from markforge.fonts import DEFAULT_FONTS


def build_styles(C: dict, F: dict | None = None) -> dict:
    """
    Build the full style sheet, themed with the resolved color dict C.
    F is an optional font mapping from register_user_fonts().
    Falls back to Helvetica/Courier built-in fonts for any role.
    """
    if F is None:
        F = DEFAULT_FONTS

    sans_reg, sans_bold, sans_ital, sans_bi = F["sans"]
    mono_reg, mono_bold, _, _            = F["mono"]
    serif_reg, serif_bold, serif_ital, _ = F["serif"]

    return {

        "cover_title": ParagraphStyle(
            "cover_title",
            fontName  = sans_bold,
            fontSize  = 30,
            leading   = 36,
            textColor = C["primary"],
            spaceAfter= 6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName  = sans_reg,
            fontSize  = 13,
            leading   = 18,
            textColor = C["muted"],
            spaceAfter= 20,
        ),

        "section_heading": ParagraphStyle(
            "section_heading",
            fontName    = sans_bold,
            fontSize    = 13,
            leading     = 17,
            textColor   = C["primary"],
            spaceBefore = 6,
            spaceAfter  = 4,
        ),

        "body": ParagraphStyle(
            "body",
            fontName  = sans_reg,
            fontSize  = 10,
            leading   = 15,
            textColor = C["text"],
            spaceAfter= 8,
            alignment = TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName    = sans_reg,
            fontSize    = 10,
            leading     = 14,
            textColor   = C["text"],
            leftIndent  = 14,
            spaceAfter  = 3,
        ),
        "note": ParagraphStyle(
            "note",
            fontName  = sans_ital,
            fontSize  = 8,
            leading   = 11,
            textColor = C["muted"],
            spaceAfter= 6,
        ),

        "highlight": ParagraphStyle(
            "highlight",
            fontName  = sans_bold,
            fontSize  = 10,
            leading   = 15,
            textColor = C["primary"],
            leftIndent= 10,
        ),

        "table_header": ParagraphStyle(
            "table_header",
            fontName  = sans_bold,
            fontSize  = 9,
            leading   = 12,
            textColor = colors.white,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName  = sans_reg,
            fontSize  = 9,
            leading   = 12,
            textColor = C["text"],
        ),

        "meta_key": ParagraphStyle(
            "meta_key",
            fontName  = sans_bold,
            fontSize  = 9,
            leading   = 13,
            textColor = C["muted"],
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName  = sans_reg,
            fontSize  = 9,
            leading   = 13,
            textColor = C["text"],
        ),

        "image_caption": ParagraphStyle(
            "image_caption",
            fontName  = sans_ital,
            fontSize  = 8,
            leading   = 10,
            textColor = colors.HexColor("#888888"),
            alignment = TA_CENTER,
            spaceAfter= 8,
        ),
    }
