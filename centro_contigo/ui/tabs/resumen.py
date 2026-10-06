"""Pestaña Resumen."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QFrame,
                               QGridLayout, QHBoxLayout, QHeaderView,
                               QLabel, QScrollArea, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from ...formato import opciones_mes
from ...servicios.resumen import calcular_resumen
from ..widgets.grafico_barras import BarChart
from ..widgets.kpi_card import KpiCard


class Resumen(QWidget):
    def __init__(self):
        super().__init__()
        self.limitado = False
        self.mes = QComboBox(); self.mes.addItems(opciones_mes())
        self.mes.setCurrentIndex(1)
        self.mes.currentTextChanged.connect(self.refresh)

        self.k_ing = KpiCard("Ingresos", "#34c759", "#30d158")
        self.k_egr = KpiCard("Egresos", "#ff3b30", "#ff453a")
        self.k_bal = KpiCard("Balance", "#0071e3", "#0a84ff")
        self.k_pen = KpiCard("Por cobrar", "#af52de", "#bf5af2")
        self.k_cli = KpiCard("Clientes activos", "#5e5ce6", "#7d7aff")
        self.k_emp = KpiCard("Personal activo", "#ff9500", "#ff9f0a")
        self.kpis = (self.k_ing, self.k_egr, self.k_bal,
                     self.k_pen, self.k_cli, self.k_emp)

        kpis = QHBoxLayout()
        for k in self.kpis:
            kpis.addWidget(k)

        top = QHBoxLayout()
        top.addWidget(QLabel("Mes:")); top.addWidget(self.mes); top.addStretch(1)

        self.lbl_chart = QLabel("<b>Flujo de caja — últimos 12 meses</b>")
        self.chart = BarChart()
        self.lbl_cta = QLabel("<b>Movimiento por cuenta</b>")
        self.t_cta = self._tbl(["Cuenta", "Ingresos", "Egresos", "Saldo"])
        self.lbl_tip = QLabel("<b>Ingresos por tipo</b>")
        self.t_tip = self._tbl(["Tipo de ingreso", "N°", "Monto"])
        self.lbl_ter = QLabel("<b>Ingresos por terapeuta</b>")
        self.t_ter = self._tbl(["Terapeuta", "N°", "Monto"])
        self.lbl_egr = QLabel("<b>Egresos por tipo</b>")
        self.t_egr = self._tbl(["Tipo de egreso", "N°", "Monto"])

        self.grid = QGridLayout()
        self.grid.addWidget(self.lbl_tip, 0, 0); self.grid.addWidget(self.t_tip, 1, 0)
        self.grid.addWidget(self.lbl_ter, 0, 1); self.grid.addWidget(self.t_ter, 1, 1)
        self.grid.addWidget(self.lbl_egr, 0, 2); self.grid.addWidget(self.t_egr, 1, 2)

        inner = QVBoxLayout()
        inner.setContentsMargins(14, 14, 14, 14); inner.setSpacing(12)
        inner.addLayout(top); inner.addLayout(kpis)
        inner.addWidget(self.lbl_chart); inner.addWidget(self.chart)
        inner.addWidget(self.lbl_cta); inner.addWidget(self.t_cta)
        inner.addLayout(self.grid)

        box = QWidget(); box.setLayout(inner)
        sc = QScrollArea(); sc.setWidget(box); sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.NoFrame)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(sc)

    def set_dark(self, dark):
        self.chart.set_dark(dark)
        for k in self.kpis:
            k.set_dark(dark)

    def set_limited(self, limitado):
        self.limitado = bool(limitado)
        self.k_egr.setVisible(not self.limitado)
        self.k_bal.setVisible(not self.limitado)
        self.k_emp.setVisible(not self.limitado)
        self.lbl_chart.setVisible(not self.limitado)
        self.chart.setVisible(not self.limitado)
        self.lbl_cta.setVisible(not self.limitado)
        self.t_cta.setVisible(not self.limitado)
        self.lbl_ter.setVisible(not self.limitado)
        self.t_ter.setVisible(not self.limitado)
        self.lbl_egr.setVisible(not self.limitado)
        self.t_egr.setVisible(not self.limitado)
        self.refresh()

    def _tbl(self, heads):
        t = QTableWidget(0, len(heads))
        t.setHorizontalHeaderLabels(heads)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setMinimumHeight(170)
        return t

    @staticmethod
    def _fill(t, rows):
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for j, v in enumerate(row):
                it = QTableWidgetItem(f"S/ {v:,.2f}" if isinstance(v, float) else str(v))
                if j:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                t.setItem(r, j, it)

    def refresh(self, *_):
        d = calcular_resumen(self.mes.currentText(), limitado=self.limitado)
        self._fill(self.t_cta, d["filas"] + [("TOTAL", d["ti"], d["te"],
                                              d["ti"] - d["te"])])
        self._fill(self.t_tip, d["tip"])
        self._fill(self.t_ter, d["ter"])
        self._fill(self.t_egr, d["tegr"])
        self.k_ing.set_value(f"S/ {d['ti']:,.2f}")
        self.k_egr.set_value(f"S/ {d['te']:,.2f}")
        self.k_bal.set_value(f"S/ {d['ti'] - d['te']:,.2f}")
        self.k_pen.set_value(f"S/ {d['pend']:,.2f}")
        self.k_cli.set_value(str(d["n_cli"]))
        self.k_emp.set_value(str(d["n_emp"]))
        if not self.limitado:
            self.chart.set_data(d["meses"],
                                [("Ingresos", "#0071e3", d["s_ing"]),
                                 ("Egresos", "#ff3b30", d["s_egr"])],
                                "Ingresos vs Egresos (12 meses)")
