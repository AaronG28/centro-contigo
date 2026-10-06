"""Esquema de tablas y migración de bases existentes."""

from .connection import db


SCHEMA = """
CREATE TABLE IF NOT EXISTS clientes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT UNIQUE, dni TEXT, nombres TEXT, apellidos TEXT,
  fecha_nacimiento TEXT, edad INTEGER, genero TEXT, orientacion_sexual TEXT,
  estado_civil TEXT, lugar_nacimiento TEXT, tiempo_residencia TEXT,
  grado_instruccion TEXT, ocupacion TEXT, religion TEXT,
  composicion_familiar TEXT, posicion_ordinal TEXT, con_quien_vive TEXT,
  telefono TEXT, email TEXT, direccion TEXT, distrito TEXT,
  modalidad_atencion TEXT,
  contacto_emergencia TEXT, telefono_emergencia TEXT,
  tratamiento_previo TEXT, enfoque_previo TEXT, motivo_abandono TEXT,
  tratamiento_psiquiatrico TEXT, medicamentos TEXT,
  diagnostico_medico TEXT, diagnostico_psicologico TEXT,
  motivo_consulta TEXT,
  como_nos_conocio TEXT, fecha_registro TEXT, activo TEXT DEFAULT 'Sí',
  notas TEXT);

CREATE TABLE IF NOT EXISTS ingresos(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT, fecha_cita TEXT, tipo TEXT,
  pagador TEXT, titular TEXT, dni TEXT, telefono TEXT,
  servicio TEXT, terapeuta TEXT, monto REAL,
  nro_citas INTEGER DEFAULT 1, status TEXT,
  cuenta TEXT, metodo TEXT,
  tipo_comprobante TEXT, comprobante TEXT, ruc TEXT,
  estado TEXT, observacion TEXT, notas TEXT);

CREATE TABLE IF NOT EXISTS egresos(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT, tipo TEXT, concepto TEXT, beneficiario TEXT,
  monto REAL, cuenta TEXT,
  tipo_comprobante TEXT, comprobante TEXT, ruc TEXT,
  notas TEXT);

CREATE TABLE IF NOT EXISTS empleados(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT UNIQUE, nombres TEXT, apellidos TEXT, dni TEXT,
  fecha_nacimiento TEXT, edad INTEGER, rol TEXT,
  telefono TEXT, email TEXT, direccion TEXT,
  fecha_ingreso TEXT, sueldo REAL, cuenta_pago TEXT,
  estado TEXT DEFAULT 'Activo', notas TEXT);

CREATE TABLE IF NOT EXISTS config(clave TEXT PRIMARY KEY, valor TEXT);

CREATE TABLE IF NOT EXISTS auditoria(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT, usuario TEXT DEFAULT '', accion TEXT, detalle TEXT);

CREATE TABLE IF NOT EXISTS usuarios(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  nombre_completo TEXT NOT NULL,
  rol TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  activo TEXT DEFAULT 'Sí',
  fecha_creacion TEXT);

CREATE INDEX IF NOT EXISTS ix_ing_fecha ON ingresos(fecha);
CREATE INDEX IF NOT EXISTS ix_egr_fecha ON egresos(fecha);
"""


def migrar_esquema():
    """Añade columnas nuevas a bases existentes sin perder datos."""
    with db() as c:
        # Auditoría: usuario (v3)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(auditoria)")}
        if "usuario" not in cols:
            c.execute("ALTER TABLE auditoria ADD COLUMN usuario TEXT DEFAULT ''")

        # Clientes: ficha clínica ampliada (v4)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(clientes)")}
        for nombre, tipo in [
            ("orientacion_sexual", "TEXT"), ("lugar_nacimiento", "TEXT"),
            ("tiempo_residencia", "TEXT"), ("grado_instruccion", "TEXT"),
            ("religion", "TEXT"), ("composicion_familiar", "TEXT"),
            ("posicion_ordinal", "TEXT"), ("con_quien_vive", "TEXT"),
            ("modalidad_atencion", "TEXT"), ("tratamiento_previo", "TEXT"),
            ("enfoque_previo", "TEXT"), ("motivo_abandono", "TEXT"),
            ("tratamiento_psiquiatrico", "TEXT"), ("medicamentos", "TEXT"),
            ("diagnostico_medico", "TEXT"), ("diagnostico_psicologico", "TEXT"),
            ("motivo_consulta", "TEXT"),
        ]:
            if nombre not in cols:
                c.execute(f"ALTER TABLE clientes ADD COLUMN {nombre} {tipo}")

        # Ingresos: campos nuevos (v4)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(ingresos)")}
        for nombre, tipo in [
            ("fecha_cita", "TEXT"), ("titular", "TEXT"), ("telefono", "TEXT"),
            ("nro_citas", "INTEGER DEFAULT 1"), ("status", "TEXT"),
            ("tipo_comprobante", "TEXT"), ("ruc", "TEXT"), ("observacion", "TEXT"),
        ]:
            if nombre not in cols:
                c.execute(f"ALTER TABLE ingresos ADD COLUMN {nombre} {tipo}")

        # Egresos: campos nuevos (v4)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(egresos)")}
        for nombre, tipo in [("tipo_comprobante", "TEXT"), ("ruc", "TEXT")]:
            if nombre not in cols:
                c.execute(f"ALTER TABLE egresos ADD COLUMN {nombre} {tipo}")


def init_db():
    """Crea las tablas si no existen y migra bases antiguas sin perder datos."""
    with db() as c:
        c.executescript(SCHEMA)
    migrar_esquema()
