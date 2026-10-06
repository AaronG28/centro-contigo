"""Arranque de la aplicación: base de datos, login y ventana principal."""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QDialog

from .config import REINICIAR_LOGIN
from .db.consultas import hay_usuarios
from .db.esquema import init_db
from .servicios.auditoria import log_action
from .ui.dialogos import LoginDialog, SetupInicialDialog
from .ui.ventana_principal import Main


def flujo_login():
    if not hay_usuarios():
        dlg = SetupInicialDialog()
        if dlg.exec() != QDialog.Accepted:
            return None
    login = LoginDialog()
    if login.exec() != QDialog.Accepted or login.usuario is None:
        return None
    return login.usuario


def main():
    # QSettings usa estos nombres: deben fijarse antes de crear la app.
    QCoreApplication.setOrganizationName("CentroContigo")
    QCoreApplication.setApplicationName("CentroContigo")
    init_db()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    while True:
        usuario = flujo_login()
        if usuario is None:
            app.quit()
            return 0
        log_action("Inicio de sesión", usuario["username"])
        win = Main(usuario)
        win.show()
        rc = app.exec()
        win.deleteLater()
        if rc != REINICIAR_LOGIN:
            return rc
