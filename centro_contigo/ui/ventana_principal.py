"""Ventana principal: pestañas, permisos, tema, copia de seguridad y cierre de sesión."""

import sqlite3
from datetime import datetime

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog,
                               QFormLayout, QLabel, QMainWindow, QMessageBox,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)

from ..config import APP_DIR, DB, REINICIAR_LOGIN, ROLES_USUARIO
from ..servicios.auditoria import log_action
from ..sesion import USUARIO_ACTUAL, cargar_permisos
from .tabs.admin import AdminTab
from .tabs.mi_cuenta import MiCuentaTab
from .tabs.modulos import (crear_tab_clientes, crear_tab_egresos,
                           crear_tab_empleados, crear_tab_ingresos)
from .tabs.resumen import Resumen
from .temas import TEMAS, build_palette, build_stylesheet


class Main(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        USUARIO_ACTUAL.update({
            "username": usuario["username"],
            "nombre": usuario["nombre_completo"],
            "rol": usuario["rol"],
        })
        self.usuario_actual = usuario
        self.permisos = cargar_permisos(usuario["rol"])

        self.setWindowTitle(
            f"Centro Contigo — {usuario['nombre_completo']} "
            f"({ROLES_USUARIO.get(usuario['rol'], usuario['rol'])})")
        self.resize(1400, 820)

        self.settings = QSettings()
        self.theme = self.settings.value("theme", "light")
        if self.theme not in TEMAS:
            self.theme = "light"

        self.resumen = Resumen()

        self.clientes = crear_tab_clientes()
        self.ingresos = crear_tab_ingresos()
        self.egresos = crear_tab_egresos()
        self.empleados = crear_tab_empleados()

        self.cruds = (self.clientes, self.ingresos, self.egresos, self.empleados)
        self.ingresos.on_change = self.resumen.refresh
        self.egresos.on_change = self.resumen.refresh
        self.clientes.on_change = lambda: (self.resumen.refresh(),
                                           self.ingresos.refresh())
        self.empleados.on_change = lambda: (self.resumen.refresh(),
                                            self.ingresos.refresh(),
                                            self.egresos.refresh())

        self.admin_tab = AdminTab(self)
        self.mi_cuenta = MiCuentaTab(self)

        # ── Ajustes (tema) ──
        self.cb_tema = QComboBox()
        self.cb_tema.addItem("☀  Claro", "light")
        self.cb_tema.addItem("🌙  Oscuro", "dark")
        self.cb_tema.setCurrentIndex(self.cb_tema.findData(self.theme))
        self.cb_tema.currentIndexChanged.connect(
            lambda: self.set_theme(self.cb_tema.currentData()))
        aj = QWidget(); al = QVBoxLayout(aj)
        al.setContentsMargins(24, 24, 24, 24); al.setAlignment(Qt.AlignTop)
        al.addWidget(QLabel("<b style='font-size:16px'>Apariencia</b>"))
        fr = QFormLayout(); fr.addRow("Tema de la aplicación:", self.cb_tema)
        al.addLayout(fr)
        n = QLabel("El tema se aplica solo a esta aplicación y no depende del modo "
                   "claro/oscuro del ordenador. Se recuerda al volver a abrirla.")
        n.setWordWrap(True); al.addWidget(n)
        self.ajustes_tab = aj

        # ── Pestañas ──
        self.tabs = QTabWidget()
        self.tabs.addTab(self.clientes,    "🧑‍💼  Clientes")
        self.tabs.addTab(self.ingresos,    "💰  Ingresos")
        self.tabs.addTab(self.egresos,     "💸  Egresos")
        self.tabs.addTab(self.empleados,   "👥  Personal")
        self.tabs.addTab(self.resumen,     "📊  Resumen")
        self.tabs.addTab(self.admin_tab,   "🛡  Administración")
        self.tabs.addTab(self.mi_cuenta,   "👤  Mi cuenta")
        self.tabs.addTab(self.ajustes_tab, "⚙  Ajustes")
        self.setCentralWidget(self.tabs)

        # ── Barra de estado ──
        self.lbl_modo = QLabel()
        self.statusBar().addPermanentWidget(self.lbl_modo)
        self.statusBar().showMessage(
            f"Sesión iniciada como {usuario['nombre_completo']} — "
            f"{ROLES_USUARIO.get(usuario['rol'], usuario['rol'])}")

        if self.permisos.get("backup"):
            btn_backup = QPushButton("💾  Copia de seguridad")
            btn_backup.setFlat(True)
            btn_backup.setCursor(Qt.PointingHandCursor)
            btn_backup.setToolTip("Guarda una copia completa de la base de datos")
            btn_backup.clicked.connect(self.backup)
            self.statusBar().addPermanentWidget(btn_backup)

        btn_logout = QPushButton("⏻  Cerrar sesión")
        btn_logout.setFlat(True)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setToolTip("Vuelve a la pantalla de inicio de sesión")
        btn_logout.clicked.connect(self.cerrar_sesion)
        self.statusBar().addPermanentWidget(btn_logout)

        # ── Menú ──
        m = self.menuBar().addMenu("Archivo")
        a1 = QAction("Crear copia de seguridad…", self)
        a1.triggered.connect(self.backup)
        a1.setEnabled(bool(self.permisos.get("backup")))
        a2 = QAction("Cerrar sesión", self)
        a2.triggered.connect(self.cerrar_sesion)
        a3 = QAction("Salir", self)
        a3.triggered.connect(lambda: QApplication.instance().exit(0))
        m.addAction(a1); m.addSeparator(); m.addAction(a2); m.addAction(a3)

        self.apply_theme()
        self.aplicar_permisos()
        self.resumen.refresh()

    def refresh_all(self):
        for t in self.cruds:
            t.refresh()
        self.resumen.refresh()

    # ── tema ──
    def apply_theme(self):
        app = QApplication.instance()
        dark = self.theme == "dark"
        try:
            app.styleHints().setColorScheme(
                Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)
        except AttributeError:
            pass
        app.setPalette(build_palette(self.theme))
        app.setStyleSheet(build_stylesheet(self.theme))
        self.resumen.set_dark(dark)

    def set_theme(self, theme):
        self.theme = theme
        self.settings.setValue("theme", theme)
        self.apply_theme()

    # ── permisos / pestañas ──
    def aplicar_permisos(self):
        p = self.permisos
        self.clientes.set_permisos(
            ver=p["ver_clientes"], crear=p["crear_clientes"],
            editar=p["editar_clientes"], eliminar=p["eliminar_clientes"],
            exportar=p.get("exportar", False))
        self.ingresos.set_permisos(
            ver=p["ver_ingresos"], crear=p["crear_ingresos"],
            editar=p["editar_ingresos"], eliminar=p["eliminar_ingresos"],
            exportar=p.get("exportar", False))
        self.egresos.set_permisos(
            ver=p["ver_egresos"], crear=p["crear_egresos"],
            editar=p["editar_egresos"], eliminar=p["eliminar_egresos"],
            exportar=p.get("exportar", False))
        self.empleados.set_permisos(
            ver=p["ver_personal"], crear=p["crear_personal"],
            editar=p["editar_personal"], eliminar=p["eliminar_personal"],
            exportar=p.get("exportar", False))

        self.tabs.setTabVisible(self.tabs.indexOf(self.egresos), bool(p["ver_egresos"]))
        self.tabs.setTabVisible(self.tabs.indexOf(self.empleados),
                                bool(p["ver_personal"]))
        self.resumen.set_limited(p.get("ver_resumen") == "limitado")
        self.admin_tab.aplicar_permisos()
        self.tabs.setTabVisible(self.tabs.indexOf(self.ajustes_tab),
                                bool(p.get("ajustes", True)))
        self.lbl_modo.setText(
            f"👤 {self.usuario_actual['nombre_completo']} · "
            f"{ROLES_USUARIO.get(self.usuario_actual['rol'], self.usuario_actual['rol'])}")

    # ── backup / logout ──
    def backup(self):
        if not self.permisos.get("backup"):
            QMessageBox.warning(self, "Acceso restringido",
                                "Tu rol no permite crear copias de seguridad.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Copia de seguridad",
            str(APP_DIR / f"respaldo_{datetime.now():%Y%m%d_%H%M}.db"),
            "Base de datos (*.db)")
        if path:
            src, dst = sqlite3.connect(DB), sqlite3.connect(path)
            try:
                src.backup(dst)
            finally:
                dst.close(); src.close()
            log_action("Creó copia de seguridad", str(path))
            QMessageBox.information(self, "Respaldo", "Copia creada correctamente.")

    def cerrar_sesion(self):
        log_action("Cerró sesión", "")
        QApplication.instance().exit(REINICIAR_LOGIN)
