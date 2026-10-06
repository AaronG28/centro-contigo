"""Gráfico de barras dibujado a mano con QPainter."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


class BarChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(250)
        self.labels, self.series, self.title, self.dark = [], [], "", False

    def set_data(self, labels, series, title=""):
        self.labels, self.series, self.title = labels, series, title
        self.update()

    def set_dark(self, dark):
        self.dark = dark; self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self.dark:
            bg, fg, grid, sub = (QColor(x) for x in
                                 ("#1c1c1e", "#f5f5f7", "#2c2c2e", "#8e8e93"))
        else:
            bg, fg, grid, sub = (QColor(x) for x in
                                 ("#ffffff", "#1c1c1e", "#eef1f5", "#8a8a8e"))
        p.fillRect(self.rect(), bg)

        top_y = 22
        if self.title:
            p.setPen(fg)
            p.setFont(QFont("Helvetica Neue", 12, QFont.DemiBold))
            p.drawText(20, top_y, self.title)

        legend_y = top_y + 12
        lx = 20
        p.setFont(QFont("Helvetica Neue", 10))
        for name, color, _ in self.series:
            p.setBrush(QColor(color)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(lx, legend_y, 12, 12, 3, 3)
            p.setPen(fg)
            p.drawText(lx + 17, legend_y + 11, name)
            lx += 18 + p.fontMetrics().horizontalAdvance(name) + 22

        left, right = 70, 20
        top = legend_y + 28
        bottom = 46
        cw, ch = w - left - right, h - top - bottom
        if cw <= 10 or ch <= 10:
            return
        if not self.labels or not self.series:
            p.setPen(sub); p.setFont(QFont("Helvetica Neue", 12))
            p.drawText(self.rect(), Qt.AlignCenter, "Sin datos disponibles")
            return

        maxv = max((max(vals) if vals else 0) for _, _, vals in self.series) or 1

        p.setFont(QFont("Helvetica Neue", 9))
        for i in range(5):
            y = top + ch * i / 4
            p.setPen(QPen(grid, 1))
            p.drawLine(left, int(y), left + cw, int(y))
            p.setPen(sub)
            p.drawText(0, int(y) - 7, left - 10, 14,
                       Qt.AlignRight | Qt.AlignVCenter,
                       f"S/ {maxv * (4 - i) / 4:,.0f}")

        n, ns = len(self.labels), len(self.series)
        group_w = cw / n
        gap = max(4, group_w * 0.15)
        inner = 3
        bar_w = max(3, max(2, group_w - 2 * gap - (ns - 1) * inner) / ns)

        for i, lab in enumerate(self.labels):
            gx = left + group_w * i
            for s, (_, color, vals) in enumerate(self.series):
                v = vals[i] if i < len(vals) else 0
                bh = ch * (v / maxv)
                x = gx + gap + s * (bar_w + inner)
                p.setBrush(QColor(color)); p.setPen(Qt.NoPen)
                p.drawRoundedRect(int(x), int(top + ch - bh),
                                  int(bar_w), int(bh), 4, 4)
            p.setPen(sub); p.setFont(QFont("Helvetica Neue", 9))
            p.drawText(int(gx), int(top + ch + 6), int(group_w), 20,
                       Qt.AlignHCenter | Qt.AlignTop, lab)
