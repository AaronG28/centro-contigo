"""Editor de datos (solo administración)."""

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from ...config import CAMPOS_INT, CAMPOS_REAL, EDITABLES, RE_FECHA
from ...db.connection import db
from ...servicios.auditoria import log_action


class DataEditor(QWidget):
    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change
        self.loading = False
        self.dirty = set()
        self.cols = []
        self.table = None

        self.sel = QComboBox(); self.sel.addItems(EDITABLES.keys())
        self.sel.currentTextChanged.connect(self.load)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔎  Buscar en la tabla…")
        self.search.textChanged.connect(self.filter)
        b_save = QPushButton("💾  Guardar cambios"); b_save.setObjectName("primary")
        b_del = QPushButton("🗑  Eliminar seleccionados"); b_del.setObjectName("danger")
        b_rel = QPushButton("↺  Recargar")
        b_save.clicked.connect(self.save_changes)
        b_del.clicked.connect(self.delete_selected)
        b_rel.clicked.connect(self.load)

        top = QHBoxLayout()
        top.addWidget(QLabel("Tabla:")); top.addWidget(self.sel)
        top.addWidget(self.search, 1)
        top.addWidget(b_rel); top.addWidget(b_save); top.addWidget(b_del)

        self.tbl = QTableWidget()
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.itemChanged.connect(self.on_item)

        hint = QLabel("Doble clic en una celda para editarla. Las celdas modificadas "
                      "se marcan en amarillo y no se guardan hasta pulsar "
                      "«Guardar cambios». Fechas: AAAA-MM-DD.")
        hint.setWordWrap(True)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(top); lay.addWidget(hint); lay.addWidget(self.tbl, 1)
        self.load()

    def load(self, *_):
        self.table = EDITABLES[self.sel.currentText()]
        with db() as c:
            self.cols = [r["name"] for r in
                         c.execute(f"PRAGMA table_info({self.table})")]
            rows = c.execute(f"SELECT * FROM {self.table} ORDER BY id DESC").fetchall()
        self.loading = True
        self.tbl.clear()
        self.tbl.setColumnCount(len(self.cols))
        self.tbl.setHorizontalHeaderLabels(self.cols)
        self.tbl.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for j, col in enumerate(self.cols):
                it = QTableWidgetItem("" if row[col] is None else str(row[col]))
                if col == "id":
                    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                self.tbl.setItem(r, j, it)
        self.tbl.resizeColumnsToContents()
        self.dirty.clear(); self.loading = False
        self.filter(self.search.text())

    def filter(self, text):
        t = (text or "").lower()
        for r in range(self.tbl.rowCount()):
            blob = " ".join(
                (self.tbl.item(r, j).text() if self.tbl.item(r, j) else "")
                for j in range(self.tbl.columnCount())).lower()
            self.tbl.setRowHidden(r, t not in blob)

    def on_item(self, it):
        if self.loading: return
        self.dirty.add((it.row(), it.column()))
        it.setBackground(QColor("#ffe58f"))
        it.setForeground(QColor("#1c1c1e"))

    def _convertir(self, col, txt):
        txt = txt.strip()
        if col in CAMPOS_REAL:
            return float(txt.replace(",", ".") or 0)
        if col in CAMPOS_INT:
            return int(txt or 0)
        if col.startswith("fecha") and txt and not RE_FECHA.match(txt):
            raise ValueError("formato de fecha inválido (use AAAA-MM-DD)")
        return txt

    def save_changes(self):
        if not self.dirty:
            QMessageBox.information(self, "Guardar", "No hay cambios por guardar.")
            return
        cambios = []
        for r, j in sorted(self.dirty):
            col = self.cols[j]
            try:
                val = self._convertir(col, self.tbl.item(r, j).text())
            except ValueError as e:
                QMessageBox.warning(self, "Revisa los datos",
                                    f"Fila {r + 1}, columna «{col}»: {e}")
                return
            cambios.append((col, val, int(self.tbl.item(r, 0).text())))
        try:
            with db() as c:
                for col, val, rid in cambios:
                    if col in self.cols and col != "id":
                        c.execute(f"UPDATE {self.table} SET {col}=? WHERE id=?",
                                  (val, rid))
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "No se pudo guardar",
                                f"Dato duplicado o inválido:\n{e}")
            return
        log_action("Edición masiva", f"{self.table}: {len(cambios)} celdas")
        self.load(); self.on_change()

    def delete_selected(self):
        filas = sorted({i.row() for i in self.tbl.selectedItems()})
        if not filas:
            QMessageBox.information(self, "Eliminar", "Selecciona una o más filas.")
            return
        if QMessageBox.question(self, "Eliminar",
                                f"¿Eliminar {len(filas)} registro(s) "
                                "definitivamente?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) != QMessageBox.Yes:
            return
        ids = [int(self.tbl.item(r, 0).text()) for r in filas]
        with db() as c:
            c.executemany(f"DELETE FROM {self.table} WHERE id=?", [(i,) for i in ids])
        log_action("Eliminó", f"{self.table}: ids {ids}")
        self.load(); self.on_change()
