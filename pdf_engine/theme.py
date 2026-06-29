"""
Theme management for the Agent PDF Engine.
"""

from reportlab.lib import colors


DEFAULT_THEME = {
    "primary": "#1A1A2E",
    "accent":  "#E94560",
    "light":   "#F5F5F5",
    "text":    "#2D2D2D",
    "muted":   "#888888",
}


def build_theme(overrides: dict | None) -> dict:
    """
    Merge user theme overrides with defaults.
    Returns a dict of color name -> reportlab Color object.
    """
    raw = {**DEFAULT_THEME, **(overrides or {})}
    return {k: colors.HexColor(v) for k, v in raw.items()}
