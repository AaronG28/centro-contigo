"""Validaciones de formularios."""


def validar_cliente(d):
    if not d["nombres"]: return "Falta el nombre del cliente."
    if d["dni"] and not d["dni"].isalnum():
        return "El DNI / CE solo debe contener letras y números."
    return None


def validar_ingreso(d):
    if not d["pagador"]: return "Indica quién realizó el pago."
    if d["monto"] <= 0: return "El monto debe ser mayor que 0."
    if not d["estado"]: return "Indica el estado del pago."
    if not d["cuenta"]: return "Indica la cuenta destino."
    return None


def validar_egreso(d):
    if not d["concepto"]: return "Falta el concepto del egreso."
    if d["monto"] <= 0: return "El monto debe ser mayor que 0."
    if not d["cuenta"]: return "Indica de qué cuenta sale el dinero."
    return None


def validar_empleado(d):
    if not d["nombres"]: return "Falta el nombre del empleado."
    if not d["rol"]: return "Indica el rol del empleado."
    return None
