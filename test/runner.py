#!/usr/bin/env python3
"""
Test runner: converts every *.md in the test/ directory to PDF,
validates output content (not just "did it crash"), and reports
pass/fail for each file.

Usage:
    python test/runner.py
"""
import re
import sys
import time
import zlib
import base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from markforge_convert import convert


# ── PDF text extraction ──────────────────────────────────────────────────


def _extract_pdf_text(pdf_path: str) -> str:
    """Return all text content from a PDF as a single string."""
    with open(pdf_path, "rb") as f:
        data = f.read()

    chunks = []
    for m in re.finditer(rb'stream\n(.+?)endstream', data, re.DOTALL):
        raw = m.group(1).strip()
        end_idx = raw.find(b'~>')
        if end_idx < 0:
            continue
        try:
            decoded = base64.a85decode(raw[:end_idx + 2], adobe=True)
            inflated = zlib.decompress(decoded)
            text = inflated.decode("latin-1")
            chunks.append(text)
        except Exception:
            continue

    return "\n".join(chunks)


# ── Expected text signatures per test file ───────────────────────────────

EXPECTED = {
    "basic.md": [
        "Table of Contents",
        "Introduction",
        "Top-Level Heading",
        "Level 1 headings",
        "Body Content",
        "Conclusion",
        "Lorem ipsum dolor sit amet",
        "Basic Smoke Test",
    ],
    "formatting.md": [
        "Bold and Italic",
        "Bold text",
        "Italic text",
        "Links",
        "Simple link",
        "Inline Code",
        "Mixed Formatting",
        "Edge Cases",
    ],
    "tables.md": [
        "Standard Table",
        "Alice Johnson",
        "Bob Smith",
        "Empty Cells",
        "Widget A",
        "Many Columns",
        "Numeric Data",
    ],
    "code.md": [
        "Python",
        "fibonacci",
        "JavaScript",
        "fetchData",
        "No Language Tag",
        "Unicode in Code",
        "Service",
        "Status",
        "Uptime",
        "web",
        "api",
        "Multiple Blocks Per Section",
        "docker build",
        "kubectl apply",
    ],
    "lists.md": [
        "Bullet List",
        "Authenticate via LDAP",
        "Authorize using RBAC",
        "Ordered List",
        "Plan the infrastructure requirements",
        "Single Item Lists",
        "Mixed Content in Section",
        "Docker",
    ],
    "comprehensive.md": [
        "Table of Contents",
        "Index",
        "1. Text Formatting",
        "2. Tabular Data",
        "3. Code Blocks",
        "4. Lists",
        "5. Callouts and Highlights",
        "6. Complex Section",
        "7. Edge Cases",
        "8. Extensive Table",
        "9. Final Section",
        "MarkForge",
        "ReportLab",
        "This document tests every feature",
        "Supercalifragilisticexpialidocious",
        "Cover page",
        "Schema validation",
    ],
}


def _check_pdf(pdf_path: str, expected: list[str]) -> list[str]:
    """Return a list of failure messages (empty = all checks passed)."""
    text = _extract_pdf_text(pdf_path)
    failures = []
    for s in expected:
        if s not in text:
            failures.append(f"Missing expected string: {s!r} not found in PDF")
    return failures


# ── Main ─────────────────────────────────────────────────────────────────


def main():
    test_dir = Path(__file__).resolve().parent
    md_files = sorted(test_dir.glob("*.md"))

    if not md_files:
        print("No test files found in test/")
        sys.exit(0)

    total = len(md_files)
    passed = 0
    failed = []

    print(f"Running {total} test(s)...\n")

    for md in md_files:
        pdf = md.with_suffix(".pdf")
        start = time.perf_counter()
        try:
            convert(str(md), str(pdf))

            expected = EXPECTED.get(md.name, [])
            failures = _check_pdf(str(pdf), expected) if expected else []

            if failures:
                elapsed = time.perf_counter() - start
                print(f"FAIL  {md.name}  ({elapsed:.2f}s)")
                for f in failures:
                    print(f"       {f}")
                failed.append(md.name)
            else:
                elapsed = time.perf_counter() - start
                print(f"  OK  {md.name}  ({elapsed:.2f}s)")
                passed += 1

        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"FAIL  {md.name}  ({elapsed:.2f}s)")
            print(f"       Exception: {e}")
            failed.append(md.name)

    print(f"\n{passed}/{total} passed", end="")
    if failed:
        print(f", {len(failed)} failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
