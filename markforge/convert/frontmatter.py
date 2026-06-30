"""
Pandoc-style YAML frontmatter parser.
"""

import re


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