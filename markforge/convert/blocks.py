"""
Block-level markdown parser.

Parses body lines into typed content blocks: paragraph, sub_heading,
highlight, code, table, bullet, ordered, task_list, definition, hr.
"""

import re

from markforge.convert.inline import inline_to_xml
from markforge.convert.tables import parse_pipe_table


def parse_content_blocks(lines: list[str], accent: str,
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

        # Blockquotes -> highlight
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