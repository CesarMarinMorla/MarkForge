"""
Deterministic Markdown → PDF converter.
Reads a markdown file (Pandoc-style YAML frontmatter), converts it to the
content dict expected by markforge.build_pdf(), and renders the PDF.

Usage:
    python -m markforge.convert file.md [output.pdf]
    markforge-convert file.md [output.pdf]

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

    # Inline code: `code` → monospace font span with light gray background
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


# ─────────────────────────────────────────────────────────────────────────────
# FRONTMATTER PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(raw_lines: list[str]) -> tuple[dict, list[str]]:
    """
    Pandoc-style YAML frontmatter parser.

    Returns (frontmatter_dict, body_lines).
    """
    frontmatter: dict[str, str] = {}
    if not raw_lines:
        return frontmatter, raw_lines

    if raw_lines[0].strip() != "---":
        return frontmatter, raw_lines

    end_idx = None
    for i in range(1, len(raw_lines)):
        if raw_lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return frontmatter, raw_lines

    for line in raw_lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^(\w[\w-]*)\s*:\s*(.*?)\s*$', line)
        if m:
            frontmatter[m.group(1)] = m.group(2)

    body = raw_lines[end_idx + 1:]
    return frontmatter, body


# ─────────────────────────────────────────────────────────────────────────────
# PIPE TABLE PARSER
# ─────────────────────────────────────────────────────────────────────────────

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

    # Determine alignment from separator line (not used currently)
    # cols = sep.split("|")[1:-1]

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


# ─────────────────────────────────────────────────────────────────────────────
# CONTENT BLOCK PARSER
# ─────────────────────────────────────────────────────────────────────────────

def _parse_content_blocks(lines: list[str], accent: str,
                          mono_font: str = "Courier") -> list[dict]:
    """
    Parse body lines into a list of content block dicts.

    Block types: paragraph, sub_heading, highlight, code, table,
    bullet, ordered, task_list, definition.
    """
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Horizontal rules
        if re.match(r'^-{3,}\s*$', line.strip()):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Blockquotes → highlight
        if line.startswith(">"):
            hl = re.sub(r'^>\s?', '', line.strip())
            hl = inline_to_xml(hl, accent, mono_font)
            blocks.append({"type": "highlight", "content": hl})
            i += 1
            continue

        # Code fences
        if line.startswith("```"):
            lang = line[3:].strip()
            code_parts = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_parts.append(lines[i].rstrip("\n"))
                i += 1
            i += 1  # skip closing ```
            code_text = "\n".join(code_parts)
            blocks.append({
                "type": "code",
                "content": code_text,
                "language": lang,
            })
            continue

        # Tables
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

        if re.match(r'^[-*]\s+\[[ x]\]\s+', line):
            task_items = []
            checked = []
            while i < len(lines) and re.match(r'^[-*]\s+\[[ x]\]\s+', lines[i].strip()):
                m = re.match(r'^[-*]\s+\[([ x])\]\s+(.*)$', lines[i].strip())
                if m:
                    checked.append(m.group(1) == "x")
                    task_items.append(inline_to_xml(m.group(2), accent, mono_font))
                i += 1
            blocks.append({"type": "task_list", "items": task_items, "checked": checked})
            continue

        if re.match(r'^[-*]\s+', line):
            bullet_items = []
            levels = []
            while i < len(lines) and re.match(r'^ *[-*]\s+', lines[i]):
                raw = lines[i]
                leading = len(raw) - len(raw.lstrip())
                level = leading // 2
                item = re.sub(r'^ *[-*]\s+', '', raw.strip())
                item = inline_to_xml(item, accent, mono_font)
                bullet_items.append(item)
                levels.append(level)
                i += 1
            blocks.append({"type": "bullet", "items": bullet_items, "levels": levels})
            continue

        if re.match(r'^\d+[.)]\s+', line):
            ordered_items = []
            o_levels = []
            while i < len(lines) and re.match(r'^ *\d+[.)]\s+', lines[i]):
                raw = lines[i]
                leading = len(raw) - len(raw.lstrip())
                level = leading // 2
                item = re.sub(r'^ *\d+[.)]\s+', '', raw.strip())
                item = inline_to_xml(item, accent, mono_font)
                ordered_items.append(item)
                o_levels.append(level)
                i += 1
            blocks.append({"type": "ordered", "items": ordered_items, "levels": o_levels})
            continue

        # Definition list: term followed by : or ~ lines
        if (i + 1 < len(lines) and lines[i + 1].strip()
                and re.match(r'^[:~]\s+', lines[i + 1].strip())):
            dterms = [inline_to_xml(line.strip(), accent, mono_font)]
            ddefs = []
            i += 1
            while i < len(lines) and lines[i].strip():
                nxt = lines[i].strip()
                m = re.match(r'^[:~]\s+(.*)$', nxt)
                if m:
                    ddefs.append(inline_to_xml(m.group(1), accent, mono_font))
                else:
                    break
                i += 1
            blocks.append({"type": "definition", "terms": dterms, "defs": ddefs})
            continue

        para = line
        j = i + 1
        while j < len(lines) and lines[j].strip():
            nxt = lines[j].strip()
            if (nxt.startswith("|") or nxt.startswith("```")
                    or nxt.startswith(">")
                    or re.match(r'^#{3,6}\s+', nxt)
                    or re.match(r'^[-*]\s+', nxt)
                    or re.match(r'^\d+[.)]\s+', nxt)
                    or re.match(r'^-{3,}\s*$', nxt)):
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

    # ── Table style ─────────────────────────────────────────────────────
    table_style = {}
    hdr_bg = frontmatter.get("table_header_bg")
    if hdr_bg and re.match(r'^#[0-9A-Fa-f]{6}$', hdr_bg):
        table_style["header_bg"] = hdr_bg
    stripe = frontmatter.get("table_stripe")
    if stripe is not None:
        table_style["stripe"] = stripe.lower() in ("true", "yes", "1")
    if table_style:
        content["table_style"] = table_style

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
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: markforge-convert <file.md> [output.pdf]")
        print("       python -m markforge.convert <file.md> [output.pdf]")
        print()
        print("Arguments:")
        print("  file.md      Path to markdown file with YAML frontmatter")
        print("  output.pdf   Optional output PDF path (defaults to file.pdf)")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help") else 1)

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
