"""Pestaña de auditoría."""

import csv
from datetime import date

from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QHBoxLayout,
                               QHeaderView, QLineEdit, QMessageBox,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from ...config import APP_DIR
from ...db.connection import db
from ...servicios.auditoria import log_action


class AuditoriaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔎  Buscar en auditoría…")
        self.search.textChanged.connect(self.filter)
        b_act = QPushButton("↺  Actualizar"); b_act.clicked.connect(self.refresh)
        b_exp = QPushButton("⤓  Exportar CSV"); b_exp.clicked.connect(self.export)
        top = QHBoxLayout()
        top.addWidget(self.search, 1); top.addWidget(b_act); top.addWidget(b_exp)

        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(
            ["Fecha", "Usuario", "Acción", "Detalle", "id"])
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tbl.horizontalHeader().setStretchLastSection(True)

        lay = QVBoxLayout(self); lay.setContentsMargins(10, 10, 10, 10)
        lay.addLayout(top); lay.addWidget(self.tbl)
        self.rows = []
        self.refresh()

    def refresh(self):
        with db() as c:
            self.rows = c.execute(
                "SELECT id, fecha, usuario, accion, detalle FROM auditoria "
                "ORDER BY id DESC LIMIT 5000").fetchall()
        self.tbl.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            for j, key in enumerate(("fecha", "usuario", "accion", "detalle", "id")):
                self.tbl.setItem(r, j, QTableWidgetItem(str(row[key] or "")))
        self.tbl.resizeColumnsToContents()
        self.filter(self.search.text())

    def filter(self, text):
        t = (text or "").lower()
        for r, row in enumerate(self.rows):
            blob = " ".join(str(row[k] or "") for k in
                            ("fecha", "usuario", "accion", "detalle")).lower()
            self.tbl.setRowHidden(r, t not in blob)

    def export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar auditoría",
            str(APP_DIR / f"auditoria_{date.today()}.csv"), "CSV (*.csv)")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.writer(f)
            wr.writerow(["fecha", "usuario", "accion", "detalle"])
            for row in self.rows:
                wr.writerow([row["fecha"], row["usuario"],
                             row["accion"], row["detalle"]])
        log_action("Exportó auditoría", str(path))
        QMessageBox.information(self, "Exportar", f"Archivo guardado en:\n{path}")
