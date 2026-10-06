"""Cálculo del resumen financiero."""

from datetime import date

from ..config import CUENTAS
from ..db.connection import db


OK = "estado NOT IN ('Anulado','Pendiente')"


def calcular_resumen(mes, limitado=False):
    p = "%" if mes == "Todos" else mes + "%"
    with db() as c:
        ing = {r[0]: r[1] for r in c.execute(
            f"SELECT cuenta, SUM(monto) FROM ingresos WHERE fecha LIKE ? AND {OK} "
            "GROUP BY cuenta", (p,))}
        if limitado:
            egr, tegr = {}, []
        else:
            egr = {r[0]: r[1] for r in c.execute(
                "SELECT cuenta, SUM(monto) FROM egresos WHERE fecha LIKE ? GROUP BY cuenta",
                (p,))}
            tegr = c.execute("SELECT tipo, COUNT(*), SUM(monto) FROM egresos "
                             "WHERE fecha LIKE ? GROUP BY tipo ORDER BY 3 DESC",
                             (p,)).fetchall()
        tip = c.execute(f"SELECT tipo, COUNT(*), SUM(monto) FROM ingresos "
                        f"WHERE fecha LIKE ? AND {OK} GROUP BY tipo ORDER BY 3 DESC",
                        (p,)).fetchall()
        ter = c.execute(f"SELECT terapeuta, COUNT(*), SUM(monto) FROM ingresos "
                        f"WHERE fecha LIKE ? AND {OK} AND terapeuta!='' "
                        "GROUP BY terapeuta ORDER BY 3 DESC", (p,)).fetchall()
        pend = c.execute("SELECT SUM(monto) FROM ingresos WHERE fecha LIKE ? "
                         "AND estado='Pendiente'", (p,)).fetchone()[0] or 0
        n_cli = c.execute("SELECT COUNT(*) FROM clientes WHERE activo='Sí'").fetchone()[0]
        n_emp = c.execute("SELECT COUNT(*) FROM empleados WHERE estado='Activo'").fetchone()[0]

        hoy = date.today()
        y, m = hoy.year, hoy.month
        claves = []
        for _ in range(12):
            claves.append(f"{y}-{m:02d}")
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        claves.reverse()
        desde = claves[0] + "-01"
        s_ing = {r[0]: r[1] for r in c.execute(
            f"SELECT substr(fecha,1,7), SUM(monto) FROM ingresos "
            f"WHERE fecha>=? AND {OK} GROUP BY 1", (desde,))}
        if limitado:
            s_egr = {}
        else:
            s_egr = {r[0]: r[1] for r in c.execute(
                "SELECT substr(fecha,1,7), SUM(monto) FROM egresos "
                "WHERE fecha>=? GROUP BY 1", (desde,))}

    cuentas = sorted(set(CUENTAS) | set(ing) | set(egr),
                     key=lambda x: (x not in CUENTAS, x or ""))
    filas = [((k or "—"), float(ing.get(k) or 0), float(egr.get(k) or 0),
              float(ing.get(k) or 0) - float(egr.get(k) or 0)) for k in cuentas]
    ti, te = sum(f[1] for f in filas), sum(f[2] for f in filas)
    conv = lambda rows: [((r[0] or "—"), r[1], float(r[2] or 0)) for r in rows]
    return dict(
        mes=mes, filas=filas, ti=ti, te=te, pend=float(pend), n_cli=n_cli, n_emp=n_emp,
        tip=conv(tip), ter=conv(ter), tegr=conv(tegr),
        meses=[f"{k[5:]}/{k[2:4]}" for k in claves],
        s_ing=[float(s_ing.get(k) or 0) for k in claves],
        s_egr=[float(s_egr.get(k) or 0) for k in claves])
