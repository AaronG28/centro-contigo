"""Formato de valores, edad y opciones de mes."""

from datetime import date, datetime


def fmt(kind, val):
    if val is None or val == "":
        return ""
    try:
        if kind == "dt":
            return datetime.strptime(val, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
        if kind in ("date", "odate"):
            return datetime.strptime(val, "%Y-%m-%d").strftime("%d/%m/%Y")
        if kind == "money":
            return f"S/ {float(val):,.2f}"
    except (ValueError, TypeError):
        pass
    return str(val)


def calcular_edad(iso):
    try:
        n = datetime.strptime(iso, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return 0
    t = date.today()
    return t.year - n.year - ((t.month, t.day) < (n.month, n.day))


def opciones_mes():
    hoy = date.today()
    y, m = hoy.year, hoy.month
    out = ["Todos"]
    for _ in range(36):
        out.append(f"{y}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out
