"""
Deterministic Markdown -> PDF converter.
Re-exports the public API for backward compatibility.
"""

from markforge.convert.cli import convert, main

__all__ = ["convert", "main"]