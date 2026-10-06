"""Usuario con sesión activa y permisos del rol."""

from .config import PERMISOS_USUARIO


USUARIO_ACTUAL = {"username": "sistema", "nombre": "Sistema", "rol": "admin"}


def cargar_permisos(rol):
    base = PERMISOS_USUARIO.get(rol) or PERMISOS_USUARIO["recepcion"]
    return dict(base)
