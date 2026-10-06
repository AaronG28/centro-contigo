"""Registro de acciones de los usuarios."""

from datetime import datetime

from ..db.connection import db
from ..sesion import USUARIO_ACTUAL


def log_action(accion, detalle):
    u = USUARIO_ACTUAL.get("nombre") or USUARIO_ACTUAL.get("username") or "sistema"
    with db() as c:
        c.execute("INSERT INTO auditoria(fecha, usuario, accion, detalle) VALUES(?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), u, accion, detalle))
