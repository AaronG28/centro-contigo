"""Tarjeta de indicador (KPI)."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class KpiCard(QFrame):
    def __init__(self, title, light_color="#0071e3", dark_color="#0a84ff"):
        super().__init__()
        self.setObjectName("kpi")
        self._lc, self._dc = light_color, dark_color
        lay = QVBoxLayout(self); lay.setContentsMargins(16, 12, 16, 12)
        t = QLabel(title.upper()); t.setObjectName("kpiTitle")
        self.value = QLabel("—"); self.value.setObjectName("kpiValue")
        lay.addWidget(t); lay.addWidget(self.value)
        self.set_dark(False)

    def set_value(self, v):
        self.value.setText(v)

    def set_dark(self, dark):
        self.value.setStyleSheet(f"color: {self._dc if dark else self._lc};")
