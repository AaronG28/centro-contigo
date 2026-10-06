"""Pestaña «Mi cuenta» (cambio de contraseña)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFormLayout, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)

from ...config import ROLES_USUARIO
from ...db.connection import db
from ...seguridad import check_pw, hash_pw
from ...servicios.auditoria import log_action
from ...sesion import USUARIO_ACTUAL


class MiCuentaTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 24, 24, 24)
        lay.setAlignment(Qt.AlignTop)

        self.lbl_info = QLabel()
        self.lbl_info.setWordWrap(True)
        lay.addWidget(self.lbl_info); lay.addSpacing(12)

        lay.addWidget(QLabel("<b>Cambiar contraseña</b>"))
        form = QFormLayout()
        self.pw_actual = QLineEdit(); self.pw_actual.setEchoMode(QLineEdit.Password)
        self.pw_nueva = QLineEdit(); self.pw_nueva.setEchoMode(QLineEdit.Password)
        self.pw_conf = QLineEdit(); self.pw_conf.setEchoMode(QLineEdit.Password)
        form.addRow("Contraseña actual:", self.pw_actual)
        form.addRow("Nueva contraseña:", self.pw_nueva)
        form.addRow("Confirmar nueva:", self.pw_conf)
        lay.addLayout(form)
        b = QPushButton("Actualizar contraseña"); b.setObjectName("primary")
        b.clicked.connect(self.cambiar)
        lay.addWidget(b, alignment=Qt.AlignLeft)
        self.refresh()

    def refresh(self):
        u = USUARIO_ACTUAL
        self.lbl_info.setText(
            f"<h2 style='margin:0'>Hola, {u.get('nombre','—')}</h2>"
            f"<p style='color:#8e8e93;margin-top:4px'>Usuario: "
            f"<b>{u.get('username','—')}</b> · Rol: "
            f"<b>{ROLES_USUARIO.get(u.get('rol'), u.get('rol','—'))}</b></p>")

    def cambiar(self):
        with db() as c:
            r = c.execute("SELECT password_hash FROM usuarios WHERE username=?",
                          (USUARIO_ACTUAL["username"],)).fetchone()
        if not r or not check_pw(self.pw_actual.text(), r["password_hash"]):
            QMessageBox.warning(self, "Contraseña",
                                "La contraseña actual es incorrecta.")
            return
        if len(self.pw_nueva.text()) < 6:
            QMessageBox.warning(self, "Contraseña", "Mínimo 6 caracteres."); return
        if self.pw_nueva.text() != self.pw_conf.text():
            QMessageBox.warning(self, "Contraseña", "No coinciden."); return
        with db() as c:
            c.execute("UPDATE usuarios SET password_hash=? WHERE username=?",
                      (hash_pw(self.pw_nueva.text()), USUARIO_ACTUAL["username"]))
        log_action("Cambió su contraseña", USUARIO_ACTUAL["username"])
        self.pw_actual.clear(); self.pw_nueva.clear(); self.pw_conf.clear()
        QMessageBox.information(self, "Contraseña", "Contraseña actualizada.")
