"""Configuración y constantes de la aplicación (rutas, catálogos, permisos)."""

import re
from pathlib import Path


APP_DIR = Path.home() / "CentroContigo"
APP_DIR.mkdir(exist_ok=True)
DB = APP_DIR / "centro_contigo.db"

# ── Cuentas (dinero entra/sale aquí) ──
CUENTAS = ["Efectivo", "Cuenta Janyna", "Cuenta Giezi", "Cuenta Centro Contigo"]

# ── Tipos de ingreso ──
TIPOS_INGRESO = [
    "Consulta / Terapia", "Psicoterapia", "Orientación psicológica",
    "Psiquiatría", "Evaluación psicológica", "Evaluación emocional",
    "Informe psicológico", "Constancia / documento", "Terapia de pareja",
    "Renta de consultorio", "Taller DBT", "Taller DBT social",
    "Acompañamiento", "Venta de libros / manuales", "Préstamo recibido",
    "Otros ingresos",
]

# ── Servicios ──
SERVICIOS = [
    "Psicoterapia", "Consulta psicológica individual", "Terapia de pareja",
    "Terapia familiar", "Terapia infantil / adolescente",
    "Evaluación psicológica", "Evaluación emocional",
    "Orientación psicológica", "Psicoterapia grupal",
    "Orientación vocacional", "Informe psicológico", "Constancia psicológica",
    "Psiquiatría", "Taller DBT", "Taller DBT social", "Acompañamiento",
    "Manual DBT / Libros", "Renta de consultorio", "Alquiler",
    "Administración (ADM)", "Préstamo", "Otro",
]

METODOS_PAGO = ["Efectivo", "Yape", "Plin", "Transferencia", "Tarjeta",
                "Izipay", "PayPal", "Otro"]
ESTADOS_PAGO = ["Pagado", "Pendiente", "Anulado"]
ESTADOS_PACIENTE = ["NUEVO", "REGULAR"]
TIPOS_COMPROBANTE = ["", "Boleta electrónica", "Factura electrónica",
                     "Recibo por honorarios", "Ticket de venta",
                     "Nota de venta", "Sin comprobante"]

# ── Tipos de egreso ──
TIPOS_EGRESO = [
    "Servicios (luz, agua, internet)", "Alquiler del local",
    "Nómina / Sueldos", "Honorarios profesionales",
    "Materiales / tests psicológicos", "Marketing / publicidad",
    "Mantenimiento / remodelación", "Impuestos (SUNAT)",
    "Comisiones bancarias / ITF", "Capacitación", "Limpieza",
    "Movilidad / combustible", "Alimentos", "Préstamo otorgado", "Otros",
]

ROLES = ["Psicólogo(a)", "Administración", "Recepción", "Limpieza",
         "Marketing", "Otro"]
GENEROS = ["Femenino", "Masculino", "Otro", "Prefiero no decir"]
ORIENTACIONES = ["Heterosexual", "Homosexual", "Bisexual", "Pansexual",
                 "Prefiero no decir", "Otro"]
ESTADOS_CIVILES = ["Soltero(a)", "Casado(a)", "Conviviente", "Divorciado(a)",
                   "Viudo(a)", "En pareja", "Separada", "Otro"]
GRADOS_INSTRUCCION = ["Sin instrucción", "Primaria incompleta",
                      "Primaria completa", "Secundaria incompleta",
                      "Secundaria completa", "Técnico incompleto",
                      "Técnico completo", "Universitario incompleto",
                      "Universitario completo", "Postgrado", "Otro"]
MODALIDADES = ["Presencial", "Virtual", "Híbrido", "Presencial, Híbrido",
               "Virtual, Presencial", "Otro"]
COMO_NOS_CONOCIO = ["Recomendación", "Redes sociales", "Google", "TikTok",
                    "Instagram", "Facebook", "Volante", "Paciente recurrente",
                    "Referido por otro profesional", "Otro"]
TRATAMIENTO_PSIQ = ["", "Nunca", "Actualmente no, pero anteriormente sí",
                    "Sí, actualmente recibo"]

# ── Roles de usuario del sistema ──
ROLES_USUARIO = {
    "admin":     "Administrador",
    "director":     "Directora",
    "psicologo": "Psicólogo(a)",
    "recepcion": "Recepción",
}

USUARIOS_INICIALES = [
    ("giezi",  "Giezi",  "admin"),
    ("janyna", "Janyna", "director"),
    ("paola",  "Paola",  "recepcion"),
]

# Permisos por rol (granular por acción)
PERMISOS_USUARIO = {
    "admin": {
        "ver_clientes": True, "crear_clientes": True,
        "editar_clientes": True, "eliminar_clientes": True,
        "ver_ingresos": True, "crear_ingresos": True,
        "editar_ingresos": True, "eliminar_ingresos": True,
        "ver_egresos": True, "crear_egresos": True,
        "editar_egresos": True, "eliminar_egresos": True,
        "ver_personal": True, "crear_personal": True,
        "editar_personal": True, "eliminar_personal": True,
        "ver_resumen": "completo",
        "exportar": True, "informes": True, "auditoria": True,
        "usuarios": True, "backup": True, "ajustes": True,
    },
    "director": {
        "ver_clientes": True, "crear_clientes": True,
        "editar_clientes": True, "eliminar_clientes": False,
        "ver_ingresos": True, "crear_ingresos": True,
        "editar_ingresos": True, "eliminar_ingresos": False,
        "ver_egresos": True, "crear_egresos": True,
        "editar_egresos": True, "eliminar_egresos": False,
        "ver_personal": True, "crear_personal": True,
        "editar_personal": True, "eliminar_personal": False,
        "ver_resumen": "completo",
        "exportar": True, "informes": True, "auditoria": False,
        "usuarios": False, "backup": False, "ajustes": True,
    },
    "psicologo": {
        "ver_clientes": True, "crear_clientes": True,
        "editar_clientes": True, "eliminar_clientes": False,
        "ver_ingresos": True, "crear_ingresos": True,
        "editar_ingresos": True, "eliminar_ingresos": False,
        "ver_egresos": True, "crear_egresos": False,
        "editar_egresos": False, "eliminar_egresos": False,
        "ver_personal": True, "crear_personal": False,
        "editar_personal": False, "eliminar_personal": False,
        "ver_resumen": "completo",
        "exportar": True, "informes": True, "auditoria": False,
        "usuarios": False, "backup": False, "ajustes": True,
    },
    "recepcion": {
        "ver_clientes": True, "crear_clientes": True,
        "editar_clientes": True, "eliminar_clientes": False,
        "ver_ingresos": True, "crear_ingresos": True,
        "editar_ingresos": False, "eliminar_ingresos": False,
        "ver_egresos": False, "crear_egresos": False,
        "editar_egresos": False, "eliminar_egresos": False,
        "ver_personal": False, "crear_personal": False,
        "editar_personal": False, "eliminar_personal": False,
        "ver_resumen": "limitado",
        "exportar": False, "informes": False, "auditoria": False,
        "usuarios": False, "backup": False, "ajustes": True,
    },
}

# Listas cerradas → sin inyección SQL
EDITABLES = {"Clientes": "clientes", "Ingresos": "ingresos",
             "Egresos": "egresos", "Personal": "empleados"}
EXPORTABLES = {**EDITABLES, "Auditoría": "auditoria"}

CAMPOS_REAL = {"monto", "sueldo"}
CAMPOS_INT = {"edad"}
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$")

# Código de salida especial para "cerrar sesión → volver al login"
REINICIAR_LOGIN = 100
