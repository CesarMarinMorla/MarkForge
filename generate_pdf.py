#!/usr/bin/env python3
"""
Simple wrapper: converts a markdown file to PDF.
If no arguments, converts the default informe.

Usage:
    python generate_pdf.py [input.md] [output.pdf]
"""
import sys
from md2pdf import convert

if __name__ == "__main__":
    md_path = sys.argv[1] if len(sys.argv) > 1 else "informe-inventario-itu.md"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "informe-inventario-itu.pdf"
    result = convert(md_path, out_path)
    print(f"PDF generado en: {result}")
