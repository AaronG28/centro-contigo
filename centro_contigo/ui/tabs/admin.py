"""Pestaña de administración (informes, editor, auditoría, usuarios)."""

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QLabel,
                               QMessageBox, QPushButton, QStackedWidget,
                               QTabWidget, QVBoxLayout, QWidget)

from ...config import APP_DIR
from ...formato import opciones_mes
from ...servicios.auditoria import log_action
from ...servicios.exportacion import exportar_excel, exportar_pdf
from .auditoria import AuditoriaTab
from .editor_datos import DataEditor
from .usuarios import UsuariosTab


class AdminTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.stack = QStackedWidget()

        # Página bloqueada
        lock = QWidget()
        ll = QVBoxLayout(lock); ll.setAlignment(Qt.AlignCenter)
        t = QLabel("🔒  Área restringida"); t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:22px; font-weight:700;")
        s = QLabel("Tu rol no tiene acceso a esta sección.")
        s.setAlignment(Qt.AlignCenter)
        ll.addWidget(t); ll.addWidget(s)

        # Panel con sub-pestañas
        self.panel = QWidget()
        self.subtabs = QTabWidget()

        # ── Informes y respaldos ──
        info = QWidget()
        il = QVBoxLayout(info); il.setContentsMargins(14, 14, 14, 14)
        il.setSpacing(12)
        self.per = QComboBox(); self.per.addItems(opciones_mes())
        self.per.setCurrentIndex(1)
        b_pdf = QPushButton("📄  Descargar informe (PDF)")
        b_pdf.setObjectName("primary")
        b_xls = QPushButton("📊  Descargar Excel con todos los datos")
        b_bk = QPushButton("💾  Crear copia de seguridad (.db)")
        b_pdf.clicked.connect(self.pdf)
        b_xls.clicked.connect(self.excel)
        b_bk.clicked.connect(self.main.backup)
        row = QHBoxLayout()
        row.addWidget(QLabel("Periodo del informe:")); row.addWidget(self.per)
        row.addWidget(b_pdf); row.addWidget(b_xls); row.addWidget(b_bk)
        row.addStretch(1)
        il.addLayout(row)
        il.addWidget(QLabel("El informe PDF y el Excel incluyen todos los módulos "
                            "del sistema (clientes, ingresos, egresos, personal y "
                            "auditoría)."))
        il.addStretch(1)

        # ── Editor de datos ──
        ed = QWidget()
        el = QVBoxLayout(ed); el.setContentsMargins(0, 0, 0, 0)
        self.editor = DataEditor(main.refresh_all)
        el.addWidget(self.editor)

        # ── Auditoría ──
        self.auditoria = AuditoriaTab()

        # ── Usuarios ──
        self.usuarios = UsuariosTab(main)

        self.subtabs.addTab(info, "📄  Informes y respaldos")
        self.subtabs.addTab(ed,   "✏️  Editor de datos")
        self.subtabs.addTab(self.auditoria, "📜  Auditoría")
        self.subtabs.addTab(self.usuarios,  "👤  Usuarios")

        pl = QVBoxLayout(self.panel); pl.setContentsMargins(0, 0, 0, 0)
        pl.addWidget(self.subtabs)

        self.stack.addWidget(lock)
        self.stack.addWidget(self.panel)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack)

    def aplicar_permisos(self):
        p = self.main.permisos
        puede_algo = any([p.get("informes"), p.get("auditoria"),
                          p.get("usuarios"), p.get("backup")])
        self.stack.setCurrentIndex(1 if puede_algo else 0)
        if not puede_algo: return
        self.subtabs.setTabVisible(0, bool(p.get("informes") or p.get("backup")))
        self.subtabs.setTabVisible(1, bool(p.get("usuarios")))
        self.subtabs.setTabVisible(2, bool(p.get("auditoria")))
        self.subtabs.setTabVisible(3, bool(p.get("usuarios")))
        for i in range(self.subtabs.count()):
            if self.subtabs.isTabVisible(i):
                self.subtabs.setCurrentIndex(i); break
        self.editor.load()
        self.auditoria.refresh()
        self.usuarios.refresh()

    def pdf(self):
        if not self.main.permisos.get("informes"): return
        mes = self.per.currentText()
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar informe",
            str(APP_DIR / f"informe_{mes}_{date.today()}.pdf"), "PDF (*.pdf)")
        if path:
            exportar_pdf(path, mes)
            log_action("Descargó informe PDF", mes)
            QMessageBox.information(self, "Informe", f"Informe guardado en:\n{path}")

    def excel(self):
        if not self.main.permisos.get("informes"): return
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            QMessageBox.warning(self, "Falta openpyxl",
                                "Instala la librería con:\n\npip install openpyxl")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel",
            str(APP_DIR / f"centro_contigo_{date.today()}.xlsx"), "Excel (*.xlsx)")
        if path:
            exportar_excel(path, self.per.currentText())
            log_action("Descargó Excel completo", self.per.currentText())
            QMessageBox.information(self, "Excel", f"Archivo guardado en:\n{path}")
