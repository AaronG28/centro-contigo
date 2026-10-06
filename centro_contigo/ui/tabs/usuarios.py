"""Gestión de usuarios del sistema."""

import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDialog,
                               QDialogButtonBox, QFormLayout, QHBoxLayout,
                               QHeaderView, QInputDialog, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from ...config import ROLES_USUARIO
from ...db.connection import db
from ...seguridad import hash_pw
from ...servicios.auditoria import log_action
from ...sesion import USUARIO_ACTUAL


class UsuariosTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(
            ["Usuario", "Nombre", "Rol", "Activo", "Creado"])
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        b_new = QPushButton("＋  Nuevo usuario"); b_new.setObjectName("primary")
        b_edit = QPushButton("✎  Editar / Cambiar rol")
        b_reset = QPushButton("🔑  Resetear contraseña")
        b_toggle = QPushButton("🚫  Activar / Desactivar")
        b_del = QPushButton("🗑  Eliminar"); b_del.setObjectName("danger")
        b_new.clicked.connect(self.crear)
        b_edit.clicked.connect(self.editar)
        b_reset.clicked.connect(self.reset_pw)
        b_toggle.clicked.connect(self.toggle)
        b_del.clicked.connect(self.eliminar)

        top = QHBoxLayout()
        top.addWidget(b_new); top.addWidget(b_edit); top.addWidget(b_reset)
        top.addWidget(b_toggle); top.addStretch(1); top.addWidget(b_del)

        hint = QLabel("Los usuarios con «Activo = No» no pueden iniciar sesión. "
                      "Las contraseñas se guardan con hash PBKDF2; solo se pueden "
                      "resetear, no recuperar.")
        hint.setWordWrap(True)

        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(top); lay.addWidget(hint); lay.addWidget(self.tbl, 1)
        self.rows = []
        self.refresh()

    def refresh(self):
        with db() as c:
            self.rows = c.execute("SELECT * FROM usuarios ORDER BY username").fetchall()
        self.tbl.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            vals = [row["username"], row["nombre_completo"],
                    ROLES_USUARIO.get(row["rol"], row["rol"]),
                    row["activo"] or "", row["fecha_creacion"] or ""]
            for j, v in enumerate(vals):
                self.tbl.setItem(r, j, QTableWidgetItem(str(v)))

    def _sel(self):
        sel = self.tbl.selectedItems()
        if not sel:
            QMessageBox.information(self, "Usuarios", "Selecciona un usuario.")
            return None
        return self.rows[sel[0].row()]

    def crear(self):
        dlg = UsuarioDialog(self)
        if dlg.exec() != QDialog.Accepted: return
        username, nombre, rol, pw = dlg.datos()
        try:
            with db() as c:
                c.execute("INSERT INTO usuarios(username, nombre_completo, rol, "
                          "password_hash, activo, fecha_creacion) VALUES(?,?,?,?,?,?)",
                          (username, nombre, rol, hash_pw(pw), "Sí",
                           datetime.now().strftime("%Y-%m-%d %H:%M")))
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Usuarios", f"El usuario «{username}» ya existe.")
            return
        log_action("Creó usuario", username)
        self.refresh()

    def editar(self):
        r = self._sel()
        if not r: return
        dlg = UsuarioDialog(self, usuario=r)
        if dlg.exec() != QDialog.Accepted: return
        username, nombre, rol, _ = dlg.datos()
        with db() as c:
            c.execute("UPDATE usuarios SET username=?, nombre_completo=?, rol=? "
                      "WHERE id=?", (username, nombre, rol, r["id"]))
        log_action("Editó usuario", f"id={r['id']} → {username} ({rol})")
        self.refresh()

    def reset_pw(self):
        r = self._sel()
        if not r: return
        pw1, ok = QInputDialog.getText(
            self, "Nueva contraseña",
            f"Nueva contraseña para {r['username']} (mín. 6):",
            QLineEdit.Password)
        if not ok: return
        if len(pw1) < 6:
            QMessageBox.warning(self, "Contraseña", "Mínimo 6 caracteres."); return
        pw2, ok = QInputDialog.getText(
            self, "Nueva contraseña", "Repite la contraseña:", QLineEdit.Password)
        if not ok: return
        if pw1 != pw2:
            QMessageBox.warning(self, "Contraseña", "No coinciden."); return
        with db() as c:
            c.execute("UPDATE usuarios SET password_hash=? WHERE id=?",
                      (hash_pw(pw1), r["id"]))
        log_action("Reseteó contraseña", r["username"])
        QMessageBox.information(self, "Contraseña",
                                f"Contraseña de «{r['username']}» actualizada.")

    def toggle(self):
        r = self._sel()
        if not r: return
        if r["username"] == USUARIO_ACTUAL.get("username"):
            QMessageBox.warning(self, "Usuarios",
                                "No puedes desactivar tu propio usuario.")
            return
        nuevo = "No" if (r["activo"] or "Sí") == "Sí" else "Sí"
        with db() as c:
            c.execute("UPDATE usuarios SET activo=? WHERE id=?", (nuevo, r["id"]))
        log_action("Cambió estado de usuario", f"{r['username']} → activo={nuevo}")
        self.refresh()

    def eliminar(self):
        r = self._sel()
        if not r: return
        if r["username"] == USUARIO_ACTUAL.get("username"):
            QMessageBox.warning(self, "Usuarios",
                                "No puedes eliminar tu propio usuario.")
            return
        if QMessageBox.question(self, "Eliminar usuario",
                                f"¿Eliminar definitivamente al usuario "
                                f"«{r['username']}»?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) != QMessageBox.Yes:
            return
        with db() as c:
            c.execute("DELETE FROM usuarios WHERE id=?", (r["id"],))
        log_action("Eliminó usuario", r["username"])
        self.refresh()


class UsuarioDialog(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Usuario" if usuario is None else "Editar usuario")
        self.setMinimumWidth(360)
        form = QFormLayout()
        self.ed_user = QLineEdit()
        self.ed_nombre = QLineEdit()
        self.cb_rol = QComboBox()
        for k, v in ROLES_USUARIO.items():
            self.cb_rol.addItem(v, k)
        self.ed_pw1 = QLineEdit(); self.ed_pw1.setEchoMode(QLineEdit.Password)
        self.ed_pw2 = QLineEdit(); self.ed_pw2.setEchoMode(QLineEdit.Password)
        form.addRow("Usuario:", self.ed_user)
        form.addRow("Nombre completo:", self.ed_nombre)
        form.addRow("Rol:", self.cb_rol)
        if usuario is None:
            form.addRow("Contraseña:", self.ed_pw1)
            form.addRow("Confirmar:", self.ed_pw2)
        lay = QVBoxLayout(self); lay.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setObjectName("primary")
        btns.accepted.connect(self.validar)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        if usuario is not None:
            self.ed_user.setText(usuario["username"])
            self.ed_nombre.setText(usuario["nombre_completo"])
            idx = self.cb_rol.findData(usuario["rol"])
            if idx >= 0: self.cb_rol.setCurrentIndex(idx)
            self.ed_user.setReadOnly(True)

    def validar(self):
        if not self.ed_user.text().strip():
            QMessageBox.warning(self, "Datos", "El usuario no puede estar vacío.")
            return
        if not self.ed_nombre.text().strip():
            QMessageBox.warning(self, "Datos", "El nombre no puede estar vacío.")
            return
        if self.ed_pw1.isVisible():
            if len(self.ed_pw1.text()) < 6:
                QMessageBox.warning(self, "Contraseña", "Mínimo 6 caracteres.")
                return
            if self.ed_pw1.text() != self.ed_pw2.text():
                QMessageBox.warning(self, "Contraseña", "No coinciden.")
                return
        self.accept()

    def datos(self):
        return (self.ed_user.text().strip().lower(),
                self.ed_nombre.text().strip(),
                self.cb_rol.currentData(),
                self.ed_pw1.text())
