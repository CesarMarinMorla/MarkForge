"""
Section builder from parsed markdown blocks.

Splits body lines on "# " and "## " headings, then produces section dicts
with typed blocks and backward-compatible fields (body, bullets, etc.).
"""

import re
from collections import defaultdict
from pathlib import Path

from markforge.convert.blocks import parse_content_blocks
from markforge.convert.inline import inline_to_xml


def build_sections(body_lines: list[str], accent: str,
                   mono_font: str = "Courier",
                   number_sections: bool = False,
                   base_dir: Path | None = None) -> list[dict]:
    """
    Convert parsed markdown body into a list of section dicts.

    Splits on "# " and "## " headings. Produces an ordered ``blocks`` list
    within each section preserving the original line order. Also fills
    backward-compatible fields (``body``, ``bullets``, etc.) derived from
    blocks. Sub-headings (``###`` through ``######``) become block type
    ``sub_heading`` with a numeric ``level``.
    """
    # Find all heading positions (skip lines inside fenced code blocks)
    heading_positions = []
    in_code_block = False
    for i, line in enumerate(body_lines):
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and re.match(r'^#{1,2}\s+', line):
            heading_positions.append(i)

    # Parse preamble (content before first heading) into blocks
    preamble_blocks = []
    if heading_positions:
        preamble_lines = body_lines[:heading_positions[0]]
        preamble_blocks = parse_content_blocks(
            preamble_lines, accent, mono_font, base_dir=base_dir)

    sections = []
    for idx, pos in enumerate(heading_positions):
        sec_num = idx + 1

        # Extract heading
        raw_heading = body_lines[pos]
        heading = re.sub(r'^#{1,2}\s+', '', raw_heading).strip()
        if number_sections:
            heading = f"{sec_num}. {heading}"
        heading = inline_to_xml(heading, accent, mono_font)

        # Determine end of this section
        end = heading_positions[idx + 1] if idx + 1 < len(heading_positions) else len(body_lines)

        # Collect section body lines
        sec_lines = body_lines[pos + 1:end]

        blocks = parse_content_blocks(
            sec_lines, accent, mono_font, base_dir=base_dir)

        if number_sections:
            sub_counters = defaultdict(int)
            for block in blocks:
                if block["type"] == "sub_heading":
                    level = block["level"]
                    sub_counters[level] += 1
                    for l in range(level + 1, 7):
                        sub_counters[l] = 0
                    parts = [str(sec_num)]
                    for l in range(3, level + 1):
                        parts.append(str(sub_counters[l]))
                    block["content"] = f"{'.'.join(parts)} {block['content']}"

        if idx == 0 and preamble_blocks:
            blocks = preamble_blocks + blocks

        # Build section dict with blocks + backward-compat fields
        sec = {"heading": heading, "blocks": blocks}

        body_parts = []
        bullets = []
        ordered = []
        tables = []
        codes = []
        highlight = None
        note = None

        for b in blocks:
            t = b["type"]
            if t == "paragraph":
                body_parts.append(b["content"])
            elif t == "bullet":
                bullets.extend(b["items"])
            elif t == "ordered":
                ordered.extend(b["items"])
            elif t == "table":
                tables.append(b)
            elif t == "code":
                codes.append(b["content"])
            elif t == "highlight":
                highlight = b["content"]

        if body_parts:
            sec["body"] = "<br/><br/>".join(body_parts)
        if bullets:
            sec["bullets"] = bullets
        if ordered:
            sec["ordered_list"] = ordered
        if tables:
            sec["table"] = tables[0]
            if len(tables) > 1:
                extra = "".join(
                    f"<br/><br/>{' | '.join(t['headers'])}<br/>"
                    + "<br/>".join(" | ".join(row) for row in t["rows"])
                    for t in tables[1:]
                )
                body_parts.append(extra)
        if codes:
            sec["code"] = "\n\n".join(codes)
        if highlight:
            sec["highlight"] = highlight

        sections.append(sec)

    return sections