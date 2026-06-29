"""
Deterministic Markdown → PDF converter.
Reads a markdown file (Pandoc-style YAML frontmatter), converts it to the
content dict expected by markforge.build_pdf(), and renders the PDF.

Usage:
    python markforge_convert.py informe.md [output.pdf]

No AI, no agent — pure deterministic parsing.
"""

import re
import sys
from pathlib import Path

from markforge import build_pdf


# ─────────────────────────────────────────────────────────────────────────────
# INLINE MARKDOWN → XML
# ─────────────────────────────────────────────────────────────────────────────

def inline_to_xml(text: str, accent: str = "#E94560") -> str:
    """Convert inline markdown formatting to ReportLab XML tags."""
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

    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Italic: *text* or _text_ (but not inside words or _ inside code)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)

    # Inline code: `code` → just keep as plain text (no inline monospace)
    text = re.sub(r'`([^`]+)`', r'\1', text)

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

def parse_pipe_table(lines: list[str], start: int, accent: str
                     ) -> tuple[dict | None, int]:
    """
    Try to parse a pipe table starting at lines[start].
    Returns (table_dict, next_line_index) or (None, start).
    """
    if "|" not in lines[start]:
        return None, start

    header_line = lines[start].strip()
    if not header_line.startswith("|"):
        return None, start

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
        rows.append([inline_to_xml(c, accent) for c in cells])
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

    return {"headers": headers, "rows": rows, "col_widths": col_widths}, i


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

def build_sections(body_lines: list[str], accent: str) -> list[dict]:
    """
    Convert parsed markdown body into a list of section dicts.

    Splits on "## " headings. Within each section, classifies blocks as:
      body text, bullets, ordered_list, table, code, highlight (blockquote).
    Sub-headings ("###") are treated as separate sections.
    """
    # Find all heading positions
    heading_positions = []
    for i, line in enumerate(body_lines):
        if re.match(r'^##\s+', line):
            heading_positions.append(i)

    sections = []
    for idx, pos in enumerate(heading_positions):
        # Extract heading
        raw_heading = body_lines[pos]
        heading = re.sub(r'^##+\s+', '', raw_heading).strip()
        heading = inline_to_xml(heading, accent)

        # Determine end of this section
        end = heading_positions[idx + 1] if idx + 1 < len(heading_positions) else len(body_lines)

        # Collect section body lines
        sec_lines = body_lines[pos + 1:end]

        sec = {"heading": heading}

        # Process blocks
        body_parts = []
        bullets = []
        ordered = []
        tables = []
        codes = []
        highlight = None
        note = None

        i = 0
        while i < len(sec_lines):
            line = sec_lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Horizontal rule
            if re.match(r'^---+$', line):
                i += 1
                continue

            # Blockquote → highlight (only first)
            if line.startswith(">") and highlight is None:
                hl = re.sub(r'^>\s?', '', line)
                # Collect continuation lines
                j = i + 1
                while j < len(sec_lines) and sec_lines[j].strip().startswith(">"):
                    hl += " " + re.sub(r'^>\s?', '', sec_lines[j].strip())
                    j += 1
                highlight = inline_to_xml(hl, accent)
                i = j
                continue

            # Code block (fenced)
            code, next_i = parse_code_block(sec_lines, i)
            if code is not None:
                codes.append(code)
                i = next_i
                continue

            # Table
            table, next_i = parse_pipe_table(sec_lines, i, accent)
            if table is not None:
                tables.append(table)
                i = next_i
                continue

            # Bullet list: starts with "- " or "* "
            if re.match(r'^[-*]\s+', line):
                bullet_items = []
                while i < len(sec_lines) and re.match(r'^[-*]\s+', sec_lines[i].strip()):
                    item = re.sub(r'^[-*]\s+', '', sec_lines[i].strip())
                    item = inline_to_xml(item, accent)
                    bullet_items.append(item)
                    i += 1
                bullets.extend(bullet_items)
                continue

            # Ordered list: starts with "1. " or "1) "
            if re.match(r'^\d+[.)]\s+', line):
                ordered_items = []
                while i < len(sec_lines) and re.match(r'^\d+[.)]\s+', sec_lines[i].strip()):
                    item = re.sub(r'^\d+[.)]\s+', '', sec_lines[i].strip())
                    item = inline_to_xml(item, accent)
                    ordered_items.append(item)
                    i += 1
                ordered.extend(ordered_items)
                continue

            # Regular paragraph
            para = line
            j = i + 1
            while j < len(sec_lines) and sec_lines[j].strip():
                nxt = sec_lines[j].strip()
                # Stop at table, code fence, list, heading, blockquote
                if (nxt.startswith("|") or nxt.startswith("```")
                        or re.match(r'^[-*]\s+', nxt)
                        or re.match(r'^\d+[.)]\s+', nxt)
                        or nxt.startswith(">")):
                    break
                para += " " + nxt
                j += 1

            body_parts.append(inline_to_xml(para, accent))
            i = j

        # Assign content
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
        if note:
            sec["note"] = note

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
            meta[m.group(1).lower()] = inline_to_xml(m.group(2).strip())

    if meta:
        content["meta"] = meta

    # ── Build sections ──────────────────────────────────────────────────
    content["sections"] = build_sections(body_lines, theme.get("accent", "#E94560"))

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
