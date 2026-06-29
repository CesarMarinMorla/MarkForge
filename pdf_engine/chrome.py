"""
Per-page chrome (header bar, footer, watermark) for the Agent PDF Engine.
"""

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfgen_canvas

from pdf_engine.fonts import DEFAULT_FONTS


class PageChrome:
    """
    Draws the header bar, footer, and watermark on every page.
    Uses canvas-level drawing in the onFirstPage/onLaterPages callbacks.
    """

    HEADER_H = 1.8 * cm
    FOOTER_Y  = 1.5 * cm

    def __init__(self, title: str, version: str, theme: dict, margin: float,
                 show_footer_date: bool = True, watermark: str = "",
                 hf_config: dict | None = None,
                 font_dict: dict | None = None):
        self.title           = title.upper()
        self.version         = version
        self.C               = theme
        self.margin          = margin
        self.show_footer_date = show_footer_date
        self.watermark       = watermark.upper()

        fd = font_dict or DEFAULT_FONTS
        self.font_reg = fd["sans"][0]
        self.font_bold = fd["sans"][1]
        self.font_mono = fd["mono"][0]

        hf = hf_config or {}
        h_cfg = hf.get("header", {})
        self.header_show = h_cfg.get("show", True)
        self.header_left = (h_cfg.get("left") or "").replace(
            "{title}", self.title
        ) or self.title
        self.header_right = (h_cfg.get("right") or "").replace(
            "{version}", self.version
        ) or (self.version if self.version else "")

        f_cfg = hf.get("footer", {})
        self.footer_show = f_cfg.get("show", True)
        self.footer_left   = f_cfg.get("left", "")

        if "right" in f_cfg:
            self.footer_right = f_cfg["right"]
        elif show_footer_date:
            self.footer_right = "{date}"
        else:
            self.footer_right = ""

        self.footer_center = f_cfg.get("center", "\u2014 {page} \u2014")

    def __call__(self, c: pdfgen_canvas.Canvas, doc):
        c.saveState()
        if self.watermark:
            self._watermark(c, doc)
        if self.header_show:
            self._header(c, doc)
        if self.footer_show:
            self._footer(c, doc)
        c.restoreState()

    def _watermark(self, c, doc):
        pw, ph = doc.pagesize
        c.setFillColor(colors.Color(0, 0, 0, alpha=0.08))
        c.setFont(self.font_bold, 60)
        c.saveState()
        c.translate(pw / 2, ph / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, self.watermark)
        c.restoreState()

    def _header(self, c, doc):
        pw, ph = doc.pagesize
        c.setFillColor(self.C["primary"])
        c.rect(0, ph - self.HEADER_H, pw, self.HEADER_H,
               fill=True, stroke=False)

        c.setFillColor(colors.white)
        c.setFont(self.font_bold, 10)
        bar_mid = ph - self.HEADER_H + (self.HEADER_H / 2)
        c.drawString(self.margin, bar_mid - 4, self.header_left)

        if self.header_right:
            c.setFont(self.font_reg, 8)
            c.setFillColor(colors.HexColor("#AAAACC"))
            c.drawRightString(pw - self.margin, bar_mid - 3,
                              self.header_right)

    def _footer(self, c, doc):
        pw, _ = doc.pagesize
        c.setStrokeColor(self.C["accent"])
        c.setLineWidth(1.5)
        c.line(self.margin, self.FOOTER_Y, pw - self.margin, self.FOOTER_Y)

        c.setFont(self.font_reg, 8)
        c.setFillColor(self.C["muted"])

        if self.footer_left:
            c.drawString(self.margin, self.FOOTER_Y - 10, self.footer_left)

        center = self.footer_center.replace("{page}", str(doc.page))
        c.drawCentredString(pw / 2, self.FOOTER_Y - 10, center)

        if self.footer_right:
            right = self.footer_right.replace(
                "{date}", datetime.now().strftime("%d %b %Y")
            )
            c.drawRightString(pw - self.margin, self.FOOTER_Y - 10, right)

