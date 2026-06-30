"""
CLI entry point and orchestration for markdown -> PDF conversion.
"""

import re
import sys
from pathlib import Path

from markforge import build_pdf
from markforge.convert.frontmatter import parse_frontmatter
from markforge.convert.inline import inline_to_xml
from markforge.convert.sections import build_sections
from markforge.fonts import DEFAULT_FONTS, detect_system_mono


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

    # -- Build content dict from frontmatter --------------------------------
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

    # -- Detect mono font for inline code -----------------------------------
    mono = detect_system_mono()
    mono_font = mono[0] if mono else DEFAULT_FONTS["mono"][0]

    # Meta block
    meta = {}
    if "author" in frontmatter:
        meta["author"] = frontmatter["author"]
    if "date" in frontmatter:
        meta["date"] = frontmatter["date"]
    # Also grab lines like **Key:** ...
    for line in body_lines[:5]:
        m = re.match(r'\*\*(.+?):\*\*\s*(.+)', line.strip())
        if m:
            meta[m.group(1).lower()] = inline_to_xml(m.group(2).strip(), mono_font=mono_font)

    if meta:
        content["meta"] = meta

    # -- Table style --------------------------------------------------------
    table_style = {}
    hdr_bg = frontmatter.get("table_header_bg")
    if hdr_bg and re.match(r'^#[0-9A-Fa-f]{6}$', hdr_bg):
        table_style["header_bg"] = hdr_bg
    stripe = frontmatter.get("table_stripe")
    if stripe is not None:
        table_style["stripe"] = stripe.lower() in ("true", "yes", "1")
    if table_style:
        content["table_style"] = table_style

    # -- Build sections -----------------------------------------------------
    number_sections = frontmatter.get("number_sections", "").lower() in ("true", "yes", "1")
    content["sections"] = build_sections(
        body_lines, theme.get("accent", "#E94560"), mono_font,
        number_sections=number_sections,
        base_dir=md_path.parent,
    )

    # -- Render -------------------------------------------------------------
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
        print(f"PDF generated at: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()