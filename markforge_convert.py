"""
Deterministic Markdown → PDF converter.
Reads a markdown file (Pandoc-style YAML frontmatter), converts it to the
content dict expected by markforge.build_pdf(), and renders the PDF.

Usage:
    python markforge_convert.py file.md [output.pdf]

No AI, no agent — pure deterministic parsing.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from markforge import build_pdf
from markforge.fonts import DEFAULT_FONTS, detect_system_mono


# ─────────────────────────────────────────────────────────────────────────────
# INLINE MARKDOWN → XML
# ─────────────────────────────────────────────────────────────────────────────

def inline_to_xml(text: str, accent: str = "#E94560",
                  mono_font: str = "Courier") -> str:
    """Convert inline markdown formatting to ReportLab XML tags."""
    # Index terms: <<term>> → placeholder (protect from < > escaping below)
    INDEX_MARKER = '\x00IDX:'
    text = re.sub(r'<<(.+?)>>', INDEX_MARKER + r'\1' + '\x00', text)

    # Escape XML special chars first (except within XML entities)
    text = re.sub(r'&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)
    text = text.replace("<", "&lt;").replace(">", "&gt;")

    # Images: ![alt](path) → just alt text (no image support from MD)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)

    # Links: [text](url) → <font color="..."><u><a href="url">text</a></u></font>
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

    # Inline code: `code` → monospace font span with rounded light gray
    # background. Non-breaking spaces provide margin around code text.
    _nbsp = '\u00a0'
    text = re.sub(r'`([^`]+)`',
                  rf'{_nbsp}<font face="{mono_font}" backcolor="#EDEDED">\1</font>{_nbsp}',
                  text)

    # Restore index term placeholders → <index item="term"/>
    text = re.sub(r'\x00IDX:([^\x00]+)\x00', r'<index item="\1"/>', text)

    return text


# ─────────────────────────────────────────────────────────────────────────────
# YAML FRONTMATTER
# ─────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(lines: list[str]) -> tuple[dict, list[str]]:
    """
    Parse YAML frontmatter (between --- delimiters) from the top of a
    markdown file. Returns (meta_dict, body_lines).

    Handles Pandoc-style fields:
      title, subtitle, author, date, toc, titlepage-rule-color, etc.
    """
    if not lines or lines[0].strip() != "---":
        return {}, lines

    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        end += 1

    raw = "".join(lines[1:end])
    body = lines[end + 1:] if end < len(lines) else []

    meta = {}
    # Simple YAML key:value parser (no nested, no arrays)
    for m in re.finditer(r'^(\w[\w-]*)\s*:\s*(.+)$', raw, re.MULTILINE):
        key = m.group(1)
        val = m.group(2).strip().strip('"').strip("'")
        meta[key] = val

    return meta, body


# ─────────────────────────────────────────────────────────────────────────────
# TABLE PARSING (pipe tables)
# ─────────────────────────────────────────────────────────────────────────────

def parse_pipe_table(lines: list[str], start: int, accent: str,
                     mono_font: str = "Courier") -> tuple[dict | None, int]:
    """
    Try to parse a pipe table starting at lines[start].
    Detects caption from line immediately before the table (Table: ...).
    Returns (table_dict, next_line_index) or (None, start).
    """
    if "|" not in lines[start]:
        return None, start

    header_line = lines[start].strip()
    if not header_line.startswith("|"):
        return None, start

    # Detect optional caption from line before table
    caption = None
    if start > 0:
        prev = lines[start - 1].strip()
        if prev and not prev.startswith(("|", "```", "#", ">", "-", "*")):
            m = re.match(r'^[Tt]able:?\s*(.+)$', prev)
            if m:
                caption = m.group(1).strip()
            elif not re.match(r'^(\d+[.)]\s+|[-*]\s+)$', prev):
                caption = prev

    # Extract header cells
    headers = [c.strip() for c in header_line.split("|") if c.strip()]
    if not headers:
        return None, start

    # Next line must be separator (|---|)
    if start + 1 >= len(lines):
        return None, start
    sep = lines[start + 1].strip()
    if not re.match(r'^[\s|:-]+$', sep):
        return None, start

    # Parse rows
    rows = []
    i = start + 2
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|") or "|" not in line:
            break
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if not cells:
            break
        # Normalize cell count to headers
        while len(cells) < len(headers):
            cells.append("")
        cells = cells[:len(headers)]
        rows.append([inline_to_xml(c, accent, mono_font) for c in cells])
        i += 1

    if not rows:
        return None, start

    # Calculate col_widths proportional to header length
    total = 17.0
    header_lens = [len(h) for h in headers]
    total_len = sum(header_lens) or 1
    col_widths = [max(2.0, round(total * (l / total_len), 1)) for l in header_lens]
    # Adjust last to make sum exactly total
    diff = round(total - sum(col_widths), 1)
    if col_widths:
        col_widths[-1] = round(col_widths[-1] + diff, 1)

    result = {"headers": headers, "rows": rows, "col_widths": col_widths}
    if caption:
        result["caption"] = caption
    return result, i


# ─────────────────────────────────────────────────────────────────────────────
# CODE BLOCK PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_code_block(lines: list[str], start: int) -> tuple[str | None, int]:
    """Parse a fenced code block (``` or indented with 4 spaces)."""
    line = lines[start]
    # Fenced: ``` ...
    m = re.match(r'^```(\w*)\s*$', line)
    if m:
        lang = m.group(1)
        end = start + 1
        while end < len(lines) and not lines[end].strip().startswith("```"):
            end += 1
        code = "".join(lines[start + 1:end])
        # Strip trailing newline
        code = code.rstrip("\n")
        # Remove leading blank lines
        code = re.sub(r'^\n+', '', code)
        return code, end + 1

    return None, start


# ─────────────────────────────────────────────────────────────────────────────
# SECTION BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _parse_content_blocks(lines: list[str], accent: str,
                          mono_font: str = "Courier") -> list[dict]:
    """Parse raw markdown lines into an ordered list of content block dicts."""
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if re.match(r'^---+$', line):
            i += 1
            continue

        if line.startswith(">"):
            hl = re.sub(r'^>\s?', '', line)
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith(">"):
                hl += " " + re.sub(r'^>\s?', '', lines[j].strip())
                j += 1
            blocks.append({"type": "highlight",
                           "content": inline_to_xml(hl, accent, mono_font)})
            i = j
            continue

        code, next_i = parse_code_block(lines, i)
        if code is not None:
            blocks.append({"type": "code", "content": code})
            i = next_i
            continue

        table, next_i = parse_pipe_table(lines, i, accent)
        if table is not None:
            blocks.append({"type": "table", **table})
            i = next_i
            continue

        sh = re.match(r'^(#{3,6})\s+', line)
        if sh:
            level = len(sh.group(1))
            sub = re.sub(r'^#{3,6}\s+', '', line)
            blocks.append({"type": "sub_heading",
                           "level": level,
                           "content": inline_to_xml(sub, accent, mono_font)})
            i += 1
            continue

        if re.match(r'^[-*]\s+', line):
            bullet_items = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                item = re.sub(r'^[-*]\s+', '', lines[i].strip())
                item = inline_to_xml(item, accent, mono_font)
                bullet_items.append(item)
                i += 1
            blocks.append({"type": "bullet", "items": bullet_items})
            continue

        if re.match(r'^\d+[.)]\s+', line):
            ordered_items = []
            while i < len(lines) and re.match(r'^\d+[.)]\s+', lines[i].strip()):
                item = re.sub(r'^\d+[.)]\s+', '', lines[i].strip())
                item = inline_to_xml(item, accent, mono_font)
                ordered_items.append(item)
                i += 1
            blocks.append({"type": "ordered", "items": ordered_items})
            continue

        para = line
        j = i + 1
        while j < len(lines) and lines[j].strip():
            nxt = lines[j].strip()
            if (nxt.startswith("|") or nxt.startswith("```")
                    or nxt.startswith(">")
                    or re.match(r'^#{3,6}\s+', nxt)
                    or re.match(r'^[-*]\s+', nxt)
                    or re.match(r'^\d+[.)]\s+', nxt)):
                break
            para += " " + nxt
            j += 1

        blocks.append({"type": "paragraph",
                       "content": inline_to_xml(para, accent, mono_font)})
        i = j

    return blocks


def build_sections(body_lines: list[str], accent: str,
                   mono_font: str = "Courier",
                   number_sections: bool = False) -> list[dict]:
    """
    Convert parsed markdown body into a list of section dicts.

    Splits on "# " and "## " headings. Produces an ordered ``blocks`` list
    within each section preserving the original line order. Also fills
    backward-compatible fields (``body``, ``bullets``, etc.) derived from
    blocks. Sub-headings (``###`` through ``######``) become block type
    ``sub_heading`` with a numeric ``level``.
    """
    # Find all heading positions
    heading_positions = []
    for i, line in enumerate(body_lines):
        if re.match(r'^#{1,2}\s+', line):
            heading_positions.append(i)

    # Parse preamble (content before first heading) into blocks
    preamble_blocks = []
    if heading_positions:
        preamble_lines = body_lines[:heading_positions[0]]
        preamble_blocks = _parse_content_blocks(preamble_lines, accent, mono_font)

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

        blocks = _parse_content_blocks(sec_lines, accent, mono_font)

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


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: markdown file → PDF
# ─────────────────────────────────────────────────────────────────────────────

def convert(md_path: str, output_path: str | None = None) -> str:
    """
    Convert a markdown file to PDF using MarkForge.

    Returns the output PDF path.
    """
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # Separate frontmatter from body
    frontmatter, body_lines = parse_frontmatter(raw_lines)

    # ── Build content dict from frontmatter ──────────────────────────────
    content = {}

    # Title
    content["title"] = frontmatter.get("title", md_path.stem)

    # Subtitle
    if "subtitle" in frontmatter:
        content["subtitle"] = frontmatter["subtitle"]

    # Output path
    content["output"] = output_path or md_path.with_suffix(".pdf").name

    # TOC
    if frontmatter.get("toc", "").lower() in ("true", "yes", "1"):
        content["show_toc"] = True

    # Index
    if frontmatter.get("index", "").lower() in ("true", "yes", "1"):
        content["show_index"] = True

    # Theme from titlepage-rule-color
    theme = {}
    rule_color = frontmatter.get("titlepage-rule-color", "")
    if rule_color and re.match(r'^[0-9A-Fa-f]{6}$', rule_color):
        theme["primary"] = f"#{rule_color}"
        theme["accent"] = f"#{rule_color}"
    theme.setdefault("primary", "#0D3B66")
    theme.setdefault("accent", "#E94560")
    theme.setdefault("light", "#F5F5F5")
    theme.setdefault("text", "#2D2D2D")
    theme.setdefault("muted", "#888888")
    content["theme"] = theme

    # ── Detect mono font for inline code ────────────────────────────────
    mono = detect_system_mono()
    mono_font = mono[0] if mono else DEFAULT_FONTS["mono"][0]

    # Meta block
    meta = {}
    if "author" in frontmatter:
        meta["author"] = frontmatter["author"]
    if "date" in frontmatter:
        meta["date"] = frontmatter["date"]
    # Also grab lines like **Asignaturas:** ...
    for line in body_lines[:5]:
        m = re.match(r'\*\*(.+?):\*\*\s*(.+)', line.strip())
        if m:
            meta[m.group(1).lower()] = inline_to_xml(m.group(2).strip(), mono_font=mono_font)

    if meta:
        content["meta"] = meta

    # ── Build sections ──────────────────────────────────────────────────
    number_sections = frontmatter.get("number_sections", "").lower() in ("true", "yes", "1")
    content["sections"] = build_sections(
        body_lines, theme.get("accent", "#E94560"), mono_font,
        number_sections=number_sections,
    )

    # ── Render ──────────────────────────────────────────────────────────
    output = build_pdf(content, output_path)
    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: python markforge_convert.py <file.md> [output.pdf]")
        sys.exit(1)

    md_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = convert(md_path, output_path)
        print(f"PDF generado en: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
