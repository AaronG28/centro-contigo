"""Diálogos de inicio de sesión y configuración inicial."""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox,
                               QFormLayout, QFrame, QLabel, QLineEdit,
                               QMessageBox, QVBoxLayout)

from ..config import ROLES_USUARIO, USUARIOS_INICIALES
from ..db.connection import db
from ..seguridad import check_pw, hash_pw
from ..servicios.auditoria import log_action


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Iniciar sesión — Centro Contigo")
        self.setMinimumWidth(380)
        self.usuario = None

        lay = QVBoxLayout(self)
        titulo = QLabel("<h2 style='margin:0'>Centro Contigo</h2>"
                        "<p style='color:#6e6e73;margin-top:2px'>"
                        "Inicia sesión para continuar</p>")
        titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(titulo); lay.addSpacing(6)

        form = QFormLayout()
        self.ed_user = QLineEdit()
        self.ed_user.setPlaceholderText("p. ej. giezi")
        self.ed_pass = QLineEdit()
        self.ed_pass.setEchoMode(QLineEdit.Password)
        self.ed_pass.setPlaceholderText("Contraseña")
        form.addRow("Usuario:", self.ed_user)
        form.addRow("Contraseña:", self.ed_pass)
        lay.addLayout(form)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color:#ff3b30;")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        lay.addWidget(self.lbl_error)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Iniciar sesión")
        btns.button(QDialogButtonBox.Ok).setObjectName("primary")
        btns.button(QDialogButtonBox.Cancel).setText("Salir")
        btns.accepted.connect(self.entrar)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        self.ed_pass.returnPressed.connect(self.entrar)
        self.ed_user.returnPressed.connect(self.ed_pass.setFocus)
        self.ed_user.setFocus()

    def entrar(self):
        u = self.ed_user.text().strip().lower()
        p = self.ed_pass.text()
        if not u or not p:
            self.lbl_error.setText("Ingresa usuario y contraseña.")
            return
        with db() as c:
            r = c.execute("SELECT * FROM usuarios WHERE username=?", (u,)).fetchone()
        if r is None or not check_pw(p, r["password_hash"]):
            self.lbl_error.setText("Usuario o contraseña incorrectos.")
            self.ed_pass.clear(); self.ed_pass.setFocus()
            return
        if r["activo"] != "Sí":
            self.lbl_error.setText("Este usuario está desactivado. "
                                   "Contacta al administrador.")
            return
        self.usuario = dict(r)
        self.accept()


class SetupInicialDialog(QDialog):
    """Primera ejecución: pide contraseñas para los 3 usuarios iniciales."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración inicial — Centro Contigo")
        self.setMinimumWidth(580)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "<h2 style='margin:0'>Bienvenido a Centro Contigo</h2>"
            "<p>Primera vez que se ejecuta esta versión. Define las contraseñas "
            "de los tres usuarios. No se guardan en el código: se almacenan con "
            "hash PBKDF2.</p>"))

        self.cb_mostrar = QCheckBox("👁  Mostrar contraseñas mientras escribo")
        self.cb_mostrar.toggled.connect(self._toggle_mostrar)
        lay.addWidget(self.cb_mostrar)

        self.fields = {}
        self.lbl_len = {}

        for username, nombre, rol in USUARIOS_INICIALES:
            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet("color:#d2d2d7;")
            lay.addWidget(sep)

            lay.addWidget(QLabel(f"<b style='font-size:14px'>{nombre}</b> "
                                 f"<span style='color:#8e8e93'>— {ROLES_USUARIO[rol]}"
                                 "</span>"))

            form = QFormLayout()
            form.setContentsMargins(12, 0, 0, 8)

            ed_user = QLineEdit(username); ed_user.setReadOnly(True)
            ed_user.setStyleSheet("background:#f0f0f2; color:#6e6e73; "
                                  "border:1px solid #d2d2d7;")
            form.addRow("Usuario (no editable):", ed_user)

            pw1 = QLineEdit(); pw1.setEchoMode(QLineEdit.Password)
            pw1.setPlaceholderText("Escribe la contraseña de este usuario")
            pw1.setMinimumWidth(260)
            pw1.textChanged.connect(lambda txt, u=username: self._update_len(u, txt))
            form.addRow("Contraseña:", pw1)

            pw2 = QLineEdit(); pw2.setEchoMode(QLineEdit.Password)
            pw2.setPlaceholderText("Vuelve a escribir la misma contraseña")
            form.addRow("Repetir contraseña:", pw2)

            self.fields[username] = (pw1, pw2)
            len_lbl = QLabel("0 caracteres (mínimo 6)")
            len_lbl.setStyleSheet("color:#8e8e93; margin-left:12px;")
            form.addRow("", len_lbl)
            self.lbl_len[username] = len_lbl
            lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Crear usuarios")
        btns.button(QDialogButtonBox.Ok).setObjectName("primary")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        btns.accepted.connect(self.guardar)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _toggle_mostrar(self, on):
        modo = QLineEdit.Normal if on else QLineEdit.Password
        for pw1, pw2 in self.fields.values():
            pw1.setEchoMode(modo); pw2.setEchoMode(modo)

    def _update_len(self, username, txt):
        n = len(txt)
        color = "#34c759" if n >= 6 else "#ff3b30"
        self.lbl_len[username].setText(
            f"<span style='color:{color}'>{n} caracteres</span> "
            "<span style='color:#8e8e93'>(mínimo 6)</span>")

    def guardar(self):
        errores = []
        for username, nombre, _ in USUARIOS_INICIALES:
            pw1, pw2 = self.fields[username]
            p1, p2 = pw1.text(), pw2.text()
            if p1.lower() == username.lower():
                errores.append(f"· {nombre}: pusiste el nombre de usuario "
                               "como contraseña. Elige otra distinta.")
                continue
            if len(p1) < 6:
                errores.append(f"· {nombre}: la contraseña debe tener al menos "
                               f"6 caracteres (tiene {len(p1)}).")
            elif p1 != p2:
                errores.append(f"· {nombre}: la contraseña y su repetición "
                               "no coinciden.")
        if errores:
            QMessageBox.warning(self, "Revisa las contraseñas",
                                "Corrige lo siguiente:\n\n" + "\n".join(errores))
            return

        with db() as c:
            for username, nombre, rol in USUARIOS_INICIALES:
                pw1, _ = self.fields[username]
                c.execute("INSERT INTO usuarios(username, nombre_completo, rol, "
                          "password_hash, activo, fecha_creacion) VALUES(?,?,?,?,?,?)",
                          (username, nombre, rol, hash_pw(pw1.text()), "Sí",
                           datetime.now().strftime("%Y-%m-%d %H:%M")))
        log_action("Configuración inicial", "Se crearon los usuarios por defecto")
        self.accept()
