"""
Inline markdown -> ReportLab XML conversion.
"""

import re


def inline_to_xml(text: str, accent: str = "#E94560",
                  mono_font: str = "Courier") -> str:
    """Convert inline markdown formatting to ReportLab XML tags."""
    # Index terms: <<term>> -> placeholder (protect from < > escaping below)
    INDEX_MARKER = '\x00IDX:'
    text = re.sub(r'<<(.+?)>>', INDEX_MARKER + r'\1' + '\x00', text)

    # Escape XML special chars first (except within XML entities)
    _amp = chr(38) + "amp;"
    _lt = chr(38) + "lt;"
    _gt = chr(38) + "gt;"
    text = re.sub(r'&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)', _amp, text)
    text = text.replace("<", _lt).replace(">", _gt)

    # Standalone images are parsed as blocks; inline images fall back to alt text.
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)

    # Links: [text](url) -> <font color="..."><u><a href="url">text</a></u></font>
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        rf'<font color="{accent}"><u><a href="\2">\1</a></u></font>',
        text,
    )

    # Bold + italic: ***text*** or ___text___ (must precede separate bold/italic)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)

    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Italic: *text* or _text_ (but not inside words or _ inside code)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)

    # Inline code: `code` -> monospace font span with light gray background
    _nbsp = '\u00a0'
    text = re.sub(
        r'`([^`]+)`',
        rf'{_nbsp}<font face="{mono_font}" backcolor="#EDEDED">\1</font>{_nbsp}',
        text,
    )

    # Restore index markers
    text = text.replace(INDEX_MARKER, '<index item="')
    text = text.replace('\x00', '"/>')

    # Line breaks
    text = text.replace("  \n", "<br/>")

    return text