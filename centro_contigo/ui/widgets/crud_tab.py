"""Pestaña CRUD genérica (formulario + tabla + búsqueda + CSV)."""

import csv
import sqlite3
from datetime import date

from PySide6.QtCore import QDate, QDateTime, QSettings, Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox,
    QFileDialog, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSpinBox,
    QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ...config import APP_DIR
from ...db.connection import db
from ...db.consultas import next_code
from ...formato import calcular_edad, fmt
from ...servicios.auditoria import log_action


class CrudTab(QWidget):
    def __init__(self, table, fields, cols, order, validator=None, on_change=None,
                 prefill=None, auto_code=None, combo_sources=None, form_width=400):
        super().__init__()
        self.table = table
        self.fields = fields
        self.cols = cols
        self.order = order
        self.kinds = {k: kind for k, _, kind, _ in fields}
        self.validator = validator
        self.on_change = on_change
        self.prefill = prefill
        self.auto_code = auto_code
        self.combo_sources = combo_sources or {}
        self.cur_id = None
        self.rows = []
        self.w = {}

        self.puede_ver = True
        self.puede_crear = True
        self.puede_editar = True
        self.puede_eliminar = True
        self.puede_exportar = True

        form = QFormLayout()
        form.setSpacing(9)
        form.setContentsMargins(14, 14, 14, 14)
        for key, label, kind, opts in fields:
            self.w[key] = self._make(kind, opts)
            form.addRow(label, self.w[key])
        if "fecha_nacimiento" in self.w and "edad" in self.w:
            self.w["fecha_nacimiento"].dateChanged.connect(self._sync_edad)
        box = QWidget(); box.setLayout(form)
        scroll = QScrollArea(); scroll.setWidget(box); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        # El ancho ya no es fijo: lo controla el QSplitter de abajo.

        self.b_save = QPushButton("＋  Guardar nuevo")
        self.b_upd = QPushButton("✎  Actualizar")
        self.b_del = QPushButton("🗑  Eliminar")
        self.b_new = QPushButton("↺  Limpiar")
        self.b_save.clicked.connect(lambda: self.save(False))
        self.b_upd.clicked.connect(lambda: self.save(True))
        self.b_del.clicked.connect(self.delete)
        self.b_new.clicked.connect(self.clear)
        self.b_save.setObjectName("primary")
        self.b_del.setObjectName("danger")

        left = QVBoxLayout(); left.setSpacing(8)
        left.addWidget(scroll)
        row1 = QHBoxLayout(); row1.addWidget(self.b_save); row1.addWidget(self.b_upd)
        row2 = QHBoxLayout(); row2.addWidget(self.b_del); row2.addWidget(self.b_new)
        left.addLayout(row1); left.addLayout(row2)

        self.search = QLineEdit(); self.search.setPlaceholderText("🔎  Buscar…")
        self.search.textChanged.connect(self.filter)
        self.b_exp = QPushButton("⤓  Exportar CSV")
        self.b_exp.clicked.connect(self.export)
        top = QHBoxLayout()
        top.addWidget(self.search, 1); top.addWidget(self.b_exp)

        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(
            [next(l for k, l, _, _ in fields if k == c) for c in cols])
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.itemSelectionChanged.connect(self.on_select)

        right = QVBoxLayout(); right.setSpacing(8)
        right.addLayout(top); right.addWidget(self.tbl)

        # ── QSplitter en lugar de QHBoxLayout fijo ──
        izq = QWidget(); izq.setLayout(left)
        der = QWidget(); der.setLayout(right)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)   # no colapsar a 0
        self.splitter.setHandleWidth(6)               # barra fácil de agarrar
        self.splitter.addWidget(izq)
        self.splitter.addWidget(der)
        self.splitter.setStretchFactor(0, 0)          # la ficha mantiene ancho
        self.splitter.setStretchFactor(1, 1)          # la tabla absorbe el resto
        self.splitter.setSizes([form_width, 900])     # ancho inicial razonable

        # Persistencia del ancho entre sesiones
        s = QSettings()
        sizes = s.value("crudtab/splitter_sizes")
        if sizes:
            try:
                self.splitter.setSizes([int(x) for x in sizes])
            except (TypeError, ValueError):
                pass
        self.splitter.splitterMoved.connect(
            lambda: s.setValue("crudtab/splitter_sizes", self.splitter.sizes()))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.addWidget(self.splitter)

        self.refresh(); self.clear()

    def set_permisos(self, ver=True, crear=True, editar=True,
                     eliminar=True, exportar=True):
        self.puede_ver = ver; self.puede_crear = crear
        self.puede_editar = editar; self.puede_eliminar = eliminar
        self.puede_exportar = exportar
        self.b_save.setEnabled(crear); self.b_upd.setEnabled(editar)
        self.b_del.setEnabled(eliminar); self.b_exp.setVisible(exportar)
        self.b_save.setText("＋  Guardar nuevo" if crear else "🔒  Guardar")
        self.b_upd.setText("✎  Actualizar" if editar else "🔒  Actualizar")
        self.b_del.setText("🗑  Eliminar" if eliminar else "🔒  Eliminar")

    def _make(self, kind, opts):
        if kind == "dt":
            w = QDateTimeEdit(QDateTime.currentDateTime())
            w.setDisplayFormat("dd/MM/yyyy HH:mm"); w.setCalendarPopup(True)
        elif kind == "date":
            w = QDateEdit(QDate.currentDate())
            w.setDisplayFormat("dd/MM/yyyy"); w.setCalendarPopup(True)
        elif kind == "odate":
            w = QDateEdit(); w.setDisplayFormat("dd/MM/yyyy")
            w.setCalendarPopup(True); w.setMinimumDate(QDate(1900, 1, 1))
            w.setSpecialValueText("—"); w.setDate(w.minimumDate())
        elif kind == "money":
            w = QDoubleSpinBox(); w.setMaximum(10_000_000)
            w.setDecimals(2); w.setPrefix("S/  ")
        elif kind == "int":
            w = QSpinBox(); w.setMaximum(120)
        elif kind == "area":
            w = QPlainTextEdit(); w.setFixedHeight(70)
        elif kind in ("combo", "ecombo"):
            w = QComboBox(); w.addItems(opts or []); w.setEditable(kind == "ecombo")
        else:
            w = QLineEdit()
        return w

    def _sync_edad(self, d):
        if d != self.w["fecha_nacimiento"].minimumDate():
            self.w["edad"].setValue(calcular_edad(d.toString("yyyy-MM-dd")))

    def get(self, k):
        w, kind = self.w[k], self.kinds[k]
        if kind == "dt": return w.dateTime().toString("yyyy-MM-dd HH:mm")
        if kind == "date": return w.date().toString("yyyy-MM-dd")
        if kind == "odate":
            return "" if w.date() == w.minimumDate() else w.date().toString("yyyy-MM-dd")
        if kind in ("money", "int"): return w.value()
        if kind == "area": return w.toPlainText().strip()
        if kind in ("combo", "ecombo"): return w.currentText().strip()
        return w.text().strip()

    def set(self, k, v):
        w, kind = self.w[k], self.kinds[k]
        v = "" if v is None else v
        if kind == "dt": w.setDateTime(QDateTime.fromString(str(v), "yyyy-MM-dd HH:mm"))
        elif kind == "date": w.setDate(QDate.fromString(str(v), "yyyy-MM-dd"))
        elif kind == "odate":
            d = QDate.fromString(str(v), "yyyy-MM-dd")
            w.setDate(d if d.isValid() else w.minimumDate())
        elif kind == "money": w.setValue(float(v or 0))
        elif kind == "int": w.setValue(int(v or 0))
        elif kind == "area": w.setPlainText(str(v))
        elif kind in ("combo", "ecombo"): w.setCurrentText(str(v))
        else: w.setText(str(v))

    def clear(self):
        self.cur_id = None
        self.tbl.clearSelection()
        for k, _, kind, _ in self.fields:
            if kind == "dt": self.w[k].setDateTime(QDateTime.currentDateTime())
            elif kind == "date": self.w[k].setDate(QDate.currentDate())
            elif kind == "odate": self.w[k].setDate(self.w[k].minimumDate())
            elif kind in ("money", "int"): self.w[k].setValue(0)
            elif kind == "area": self.w[k].setPlainText("")
            elif kind in ("combo", "ecombo"):
                self.w[k].setCurrentIndex(-1); self.w[k].setEditText("")
            else: self.w[k].clear()
        if self.auto_code:
            key, prefix = self.auto_code
            self.w[key].setText(next_code(self.table, prefix))
        if self.prefill:
            self.prefill(self.w)

    def save(self, update):
        if update and not self.puede_editar:
            QMessageBox.warning(self, "Acceso restringido",
                                "No tienes permiso para editar registros.")
            return
        if not update and not self.puede_crear:
            QMessageBox.warning(self, "Acceso restringido",
                                "No tienes permiso para crear registros.")
            return
        data = {k: self.get(k) for k, *_ in self.fields}
        if data.get("fecha_nacimiento"):
            data["edad"] = calcular_edad(data["fecha_nacimiento"])
        if not update and self.auto_code:
            key, prefix = self.auto_code
            if not data.get(key):
                data[key] = next_code(self.table, prefix)
        err = self.validator(data) if self.validator else None
        if err:
            QMessageBox.warning(self, "Revisa los datos", err); return
        if update and self.cur_id is None:
            QMessageBox.information(self, "Actualizar", "Selecciona un registro.")
            return
        try:
            with db() as c:
                if update:
                    sets = ",".join(f"{k}=?" for k in data)
                    c.execute(f"UPDATE {self.table} SET {sets} WHERE id=?",
                              [*data.values(), self.cur_id])
                else:
                    ks = ",".join(data)
                    c.execute(f"INSERT INTO {self.table}({ks}) "
                              f"VALUES({','.join('?' * len(data))})",
                              list(data.values()))
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "No se pudo guardar",
                                f"Dato duplicado o inválido:\n{e}")
            return
        log_action("Actualizó" if update else "Creó",
                   f"{self.table} id={self.cur_id}" if update else self.table)
        self.clear(); self.refresh()

    def delete(self):
        if not self.puede_eliminar:
            QMessageBox.warning(self, "Acceso restringido",
                                "No tienes permiso para eliminar registros.")
            return
        if self.cur_id is None: return
        if QMessageBox.question(self, "Eliminar",
                                "¿Eliminar este registro definitivamente?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) == QMessageBox.Yes:
            resumen = " | ".join(str(self.get(k)) for k in self.cols[:4])
            with db() as c:
                c.execute(f"DELETE FROM {self.table} WHERE id=?", (self.cur_id,))
            log_action("Eliminó", f"{self.table} id={self.cur_id}: {resumen}")
            self.clear(); self.refresh()

    def refresh(self):
        with db() as c:
            self.rows = c.execute(
                f"SELECT * FROM {self.table} ORDER BY {self.order} DESC, id DESC").fetchall()
        self.tbl.setUpdatesEnabled(False)
        self.tbl.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            for j, col in enumerate(self.cols):
                it = QTableWidgetItem(fmt(self.kinds[col], row[col]))
                if self.kinds[col] == "money":
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tbl.setItem(r, j, it)
        self.tbl.setUpdatesEnabled(True)
        for k, _, kind, _ in self.fields:
            if kind == "ecombo":
                cb = self.w[k]; cur = cb.currentText()
                have = {cb.itemText(i) for i in range(cb.count())}
                for v in sorted({r[k] for r in self.rows if r[k]} - have):
                    cb.addItem(v); have.add(v)
                if k in self.combo_sources:
                    for v in self.combo_sources[k]():
                        if v and v not in have:
                            cb.addItem(v); have.add(v)
                cb.setEditText(cur)
        self.filter(self.search.text())
        if self.on_change: self.on_change()

    def filter(self, text):
        t = (text or "").lower()
        for r, row in enumerate(self.rows):
            blob = " ".join(str(row[c] or "") for c in self.cols).lower()
            self.tbl.setRowHidden(r, t not in blob)

    def on_select(self):
        sel = self.tbl.selectedItems()
        if not sel: return
        row = self.rows[sel[0].row()]
        self.cur_id = row["id"]
        for k, *_ in self.fields:
            self.set(k, row[k])

    def export(self):
        if not self.puede_exportar:
            QMessageBox.warning(self, "Acceso restringido",
                                "No tienes permiso para exportar datos.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar",
            str(APP_DIR / f"{self.table}_{date.today()}.csv"), "CSV (*.csv)")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.writer(f)
            wr.writerow([k for k, *_ in self.fields])
            for row in self.rows:
                wr.writerow([row[k] for k, *_ in self.fields])
        log_action("Exportó CSV", self.table)
        QMessageBox.information(self, "Exportar", f"Archivo guardado en:\n{path}")
