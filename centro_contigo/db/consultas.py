"""Consultas sueltas reutilizadas por varias pantallas."""

from .connection import db


def next_code(table, prefix, width=3):
    with db() as c:
        rows = c.execute(f"SELECT codigo FROM {table} WHERE codigo LIKE ?",
                         (prefix + "%",)).fetchall()
    nums = [int(t) for r in rows
            if (t := (r["codigo"] or "")[len(prefix):]).isdigit()]
    return f"{prefix}{(max(nums) + 1) if nums else 1:0{width}d}"


def hay_usuarios():
    with db() as c:
        return c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0


def cfg_get(clave):
    with db() as c:
        r = c.execute("SELECT valor FROM config WHERE clave=?", (clave,)).fetchone()
    return r["valor"] if r else None


def cfg_set(clave, valor):
    with db() as c:
        c.execute("INSERT INTO config(clave, valor) VALUES(?,?) "
                  "ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor", (clave, valor))


def consultar(sql, params=()):
    with db() as c:
        return c.execute(sql, params).fetchall()


def nombres_clientes():
    """Nombre completo de cada cliente (para autocompletar pagadores)."""
    return [f"{r['nombres']} {r['apellidos'] or ''}".strip()
            for r in consultar("SELECT nombres, apellidos FROM clientes "
                               "ORDER BY apellidos, nombres")]


def nombres_personal(solo_psico):
    """Nombre completo del personal; opcionalmente solo psicólogos."""
    return [f"{r['nombres']} {r['apellidos'] or ''}".strip()
            for r in consultar("SELECT nombres, apellidos FROM empleados "
                               + ("WHERE rol='Psicólogo(a)' " if solo_psico else "")
                               + "ORDER BY nombres")]
