#!/usr/bin/env python3
"""
Test runner: converts every *.md in the test/ directory to PDF
and reports pass/fail for each file.

Usage:
    python test/runner.py
"""
import sys
import time
from pathlib import Path

# Allow running from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from markforge_convert import convert


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
            elapsed = time.perf_counter() - start
            print(f"  OK  {md.name}  ({elapsed:.2f}s)")
            passed += 1
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"FAIL  {md.name}  ({elapsed:.2f}s)")
            print(f"       {e}")
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
