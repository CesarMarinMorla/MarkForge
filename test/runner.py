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
from markforge.convert import convert


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
    "converter_features.md": [
        "Converter Features",
        "How To Use This Document",
        "Task Lists",
        "Unchecked: deploy to staging environment",
        "Checked: run security scan on release branch",
        "Nested Bullets",
        "INNER load balancer pool",
        "Nested Ordered",
        "INNER assign pod CIDR",
        "Definition Lists",
        "YAML frontmatter",
        "High-level PDF layout API",
        "Markdown Images",
        "Accent color fixture block",
        "If the block above is missing",
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


# Structural checks for features that are visible in the PDF but not plain text.

STRUCTURAL = {
    "converter_features.md": {
        "min_images": 1,
        "min_text_positions": 2,
    },
}


def _read_pdf_bytes(pdf_path: str) -> bytes:
    with open(pdf_path, "rb") as f:
        return f.read()


def _count_embedded_images(pdf_data: bytes) -> int:
    return pdf_data.count(b"/Subtype /Image")


def _count_distinct_text_x_positions(pdf_data: bytes) -> int:
    """Count distinct horizontal layout positions (proxy for list indentation)."""
    positions = set()
    for stream in re.findall(rb"stream\r?\n(.+?)endstream", pdf_data, re.DOTALL):
        try:
            end_idx = stream.find(b"~>")
            if end_idx < 0:
                continue
            decoded = base64.a85decode(stream[: end_idx + 2], adobe=True)
            text = zlib.decompress(decoded).decode("latin-1", errors="ignore")
        except Exception:
            continue
        for x in re.findall(r"1 0 0 1 (\d+(?:\.\d+)?) \d+(?:\.\d+)? cm", text):
            positions.add(round(float(x), 1))
    return len({p for p in positions if p >= 40.0})


def _check_pdf_structure(pdf_path: str, rules: dict) -> list[str]:
    data = _read_pdf_bytes(pdf_path)
    failures = []

    min_images = rules.get("min_images")
    if min_images is not None:
        count = _count_embedded_images(data)
        if count < min_images:
            failures.append(
                f"Expected at least {min_images} embedded image(s), found {count}"
            )

    min_positions = rules.get("min_text_positions")
    if min_positions is not None:
        count = _count_distinct_text_x_positions(data)
        if count < min_positions:
            failures.append(
                f"Expected at least {min_positions} distinct text x-positions "
                f"(nested layout), found {count}"
            )

    return failures


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
            failures += _check_pdf_structure(str(pdf), STRUCTURAL.get(md.name, {}))

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
