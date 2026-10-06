"""Definición declarativa de las pestañas Clientes, Ingresos, Egresos y Personal."""

from PySide6.QtCore import QDate

from ...config import (CUENTAS, COMO_NOS_CONOCIO, ESTADOS_CIVILES,
                       ESTADOS_PACIENTE, ESTADOS_PAGO, GENEROS,
                       GRADOS_INSTRUCCION, METODOS_PAGO, MODALIDADES,
                       ORIENTACIONES, ROLES, SERVICIOS, TIPOS_COMPROBANTE,
                       TIPOS_EGRESO, TIPOS_INGRESO, TRATAMIENTO_PSIQ)
from ...db.consultas import nombres_clientes, nombres_personal
from ...validaciones import (validar_cliente, validar_egreso,
                             validar_empleado, validar_ingreso)
from ..widgets.crud_tab import CrudTab


def crear_tab_clientes():
    return CrudTab(
        "clientes",
        [("codigo", "Código", "text", None),
         ("dni", "DNI / CE", "text", None),
         ("nombres", "Nombres", "text", None),
         ("apellidos", "Apellidos", "text", None),
         ("fecha_nacimiento", "Fecha de nacimiento", "odate", None),
         ("edad", "Edad", "int", None),
         ("genero", "Género", "combo", GENEROS),
         ("orientacion_sexual", "Orientación sexual", "combo", ORIENTACIONES),
         ("estado_civil", "Estado civil", "combo", ESTADOS_CIVILES),
         ("lugar_nacimiento", "Lugar de nacimiento", "text", None),
         ("tiempo_residencia", "Tiempo en Lima", "text", None),
         ("grado_instruccion", "Grado de instrucción", "combo",
          GRADOS_INSTRUCCION),
         ("ocupacion", "Ocupación", "text", None),
         ("religion", "Religión", "text", None),
         ("composicion_familiar", "Composición familiar", "area", None),
         ("posicion_ordinal", "Posición ordinal", "text", None),
         ("con_quien_vive", "¿Con quién vive?", "text", None),
         ("telefono", "Teléfono", "text", None),
         ("email", "Correo", "text", None),
         ("direccion", "Dirección", "text", None),
         ("distrito", "Distrito", "text", None),
         ("modalidad_atencion", "Modalidad de atención", "combo", MODALIDADES),
         ("contacto_emergencia", "Contacto de emergencia", "text", None),
         ("telefono_emergencia", "Teléfono de emergencia", "text", None),
         ("tratamiento_previo", "¿Tratamiento psicológico previo?",
          "combo", ["", "No", "Sí"]),
         ("enfoque_previo", "Enfoque terapéutico previo", "text", None),
         ("motivo_abandono", "Motivo de abandono previo", "text", None),
         ("tratamiento_psiquiatrico", "Tratamiento psiquiátrico",
          "combo", TRATAMIENTO_PSIQ),
         ("medicamentos", "Medicamentos actuales", "area", None),
         ("diagnostico_medico", "Diagnóstico médico", "area", None),
         ("diagnostico_psicologico", "Diagnóstico psicológico", "area", None),
         ("motivo_consulta", "Motivo de consulta", "area", None),
         ("como_nos_conocio", "¿Cómo nos conoció?", "combo", COMO_NOS_CONOCIO),
         ("fecha_registro", "Fecha de registro", "date", None),
         ("activo", "Activo", "combo", ["Sí", "No"]),
         ("notas", "Notas", "area", None)],
        ["codigo", "dni", "nombres", "apellidos", "telefono",
         "distrito", "activo", "fecha_registro"],
        "id", validar_cliente, None,
        auto_code=("codigo", "CLI-"),
        prefill=lambda w: (w["fecha_registro"].setDate(QDate.currentDate()),
                           w["activo"].setCurrentText("Sí")),
        form_width=460)


def crear_tab_ingresos():
    return CrudTab(
        "ingresos",
        [("fecha", "Fecha de abono", "date", None),
         ("fecha_cita", "Fecha de cita", "odate", None),
         ("tipo", "Tipo de ingreso", "combo", TIPOS_INGRESO),
         ("pagador", "Paciente", "ecombo", []),
         ("titular", "Titular / apoderado que paga", "ecombo", []),
         ("dni", "DNI (opcional)", "text", None),
         ("telefono", "Teléfono de contacto", "text", None),
         ("servicio", "Servicio", "ecombo", SERVICIOS),
         ("terapeuta", "Atendido por", "ecombo", []),
         ("monto", "Monto", "money", None),
         ("nro_citas", "N° de citas del pago", "int", None),
         ("status", "Status del paciente", "combo", ["", *ESTADOS_PACIENTE]),
         ("cuenta", "Cuenta destino", "combo", CUENTAS),
         ("metodo", "Método de pago", "combo", METODOS_PAGO),
         ("tipo_comprobante", "Tipo de comprobante", "combo",
          TIPOS_COMPROBANTE),
         ("comprobante", "N° comprobante / recibo", "text", None),
         ("ruc", "RUC (si es factura)", "text", None),
         ("estado", "Estado del pago", "combo", ESTADOS_PAGO),
         ("observacion", "Observación (hora, modalidad, detalle)",
          "area", None),
         ("notas", "Notas internas", "area", None)],
        ["fecha", "tipo", "pagador", "servicio", "terapeuta",
         "monto", "cuenta", "metodo", "estado"],
        "fecha", validar_ingreso, None,
        prefill=lambda w: (w["estado"].setCurrentText("Pagado"),
                           w["nro_citas"].setValue(1)),
        combo_sources={
            "pagador": nombres_clientes,
            "titular": nombres_clientes,
            "terapeuta": lambda: nombres_personal(True)},
        form_width=460)


def crear_tab_egresos():
    return CrudTab(
        "egresos",
        [("fecha", "Fecha", "date", None),
         ("tipo", "Tipo de egreso", "combo", TIPOS_EGRESO),
         ("concepto", "Concepto", "text", None),
         ("beneficiario", "Pagado a (proveedor / personal)", "ecombo", []),
         ("monto", "Monto", "money", None),
         ("cuenta", "Sale de la cuenta", "combo", CUENTAS),
         ("tipo_comprobante", "Tipo de comprobante", "combo",
          TIPOS_COMPROBANTE),
         ("comprobante", "N° comprobante / recibo", "text", None),
         ("ruc", "RUC del proveedor", "text", None),
         ("notas", "Notas", "area", None)],
        ["fecha", "tipo", "concepto", "beneficiario",
         "monto", "cuenta", "comprobante"],
        "fecha", validar_egreso,
        combo_sources={"beneficiario": lambda: nombres_personal(False)},
        form_width=460)


def crear_tab_empleados():
    return CrudTab(
        "empleados",
        [("codigo", "Código", "text", None),
         ("nombres", "Nombres", "text", None),
         ("apellidos", "Apellidos", "text", None),
         ("dni", "DNI", "text", None),
         ("fecha_nacimiento", "Fecha de nacimiento", "odate", None),
         ("edad", "Edad", "int", None),
         ("rol", "Rol / Puesto", "combo", ROLES),
         ("telefono", "Teléfono", "text", None),
         ("email", "Correo", "text", None),
         ("direccion", "Dirección", "text", None),
         ("fecha_ingreso", "Fecha de ingreso", "date", None),
         ("sueldo", "Sueldo base", "money", None),
         ("cuenta_pago", "Cuenta de pago", "combo", CUENTAS),
         ("estado", "Estado", "combo", ["Activo", "Inactivo", "Vacaciones"]),
         ("notas", "Notas", "area", None)],
        ["codigo", "nombres", "apellidos", "rol", "telefono",
         "fecha_ingreso", "sueldo", "estado"],
        "id", validar_empleado, None,
        auto_code=("codigo", "EMP-"),
        prefill=lambda w: (w["fecha_ingreso"].setDate(QDate.currentDate()),
                           w["estado"].setCurrentText("Activo")))
