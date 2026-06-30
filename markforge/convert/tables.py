"""
Pipe table parser for markdown tables.
"""

import re

from markforge.convert.inline import inline_to_xml


def parse_pipe_table(lines: list[str], start: int,
                     accent: str) -> tuple[dict | None, int]:
    """
    Parse a pipe table starting at ``lines[start]``.

    Returns (table_dict, next_line_index) or (None, start) if not a table.
    """
    if start >= len(lines):
        return None, start

    # Check for optional caption: "Table: ..." on the line before
    caption = None
    cap_start = start
    if start > 0:
        cm = re.match(r'^Table:\s+(.+)$', lines[start - 1].strip())
        if cm:
            caption = cm.group(1)
            cap_start = start

    if not re.match(r'^\|', lines[start].strip()):
        return None, start

    # Raw header line (first non-empty after caption)
    raw_header = lines[start].strip()
    headers = [h.strip() for h in raw_header.split("|")[1:-1]]

    if not headers:
        return None, start

    # Separator line
    if start + 1 >= len(lines):
        return None, start

    sep = lines[start + 1].strip()
    if not re.match(r'^\|[-:| ]+\|$', sep):
        return None, start

    # Data rows
    rows = []
    i = start + 2
    while i < len(lines) and re.match(r'^\|', lines[i].strip()):
        cells = [
            inline_to_xml(c.strip(), accent=accent)
            for c in lines[i].split("|")[1:-1]
        ]
        # Pad or truncate to match header count
        while len(cells) < len(headers):
            cells.append("")
        cells = cells[:len(headers)]
        rows.append(cells)
        i += 1

    # Calculate proportional column widths
    lens = [max(len(h), 1) for h in headers]
    total = sum(lens)
    col_widths = [round(l / total, 3) for l in lens]

    result = {
        "headers": headers,
        "rows": rows,
        "col_widths": col_widths,
    }
    if caption:
        result["caption"] = caption

    return result, i