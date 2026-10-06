# Centro Contigo

Sistema de gestión (PySide6 + SQLite) del Centro Contigo: clientes, ingresos, egresos, personal, resumen financiero, usuarios con roles y auditoría.

## Ejecutar

```bash
pip install -r requirements.txt
python main.py          # o: python -m centro_contigo
```

Los datos se guardan en `~/CentroContigo/centro_contigo.db`.

## Estructura

```
main.py                         punto de entrada
centro_contigo/
├── config.py                   rutas, catálogos (cuentas, tipos, roles) y permisos por rol
├── sesion.py                   usuario con sesión activa y permisos
├── formato.py                  fmt(), calcular_edad(), opciones_mes()
├── seguridad.py                hash/verificación de contraseñas (PBKDF2)
├── validaciones.py             validar_cliente / ingreso / egreso / empleado
├── app.py                      arranque: init_db → login → ventana principal
├── db/
│   ├── connection.py           db(): conexión que siempre se cierra
│   ├── esquema.py              SCHEMA, migración de columnas, init_db()
│   └── consultas.py            next_code, nombres_clientes/personal, cfg_get/set
├── servicios/                  lógica sin interfaz
│   ├── resumen.py              calcular_resumen()
│   ├── exportacion.py          exportar_excel(), exportar_pdf()
│   └── auditoria.py            log_action()
└── ui/
    ├── temas.py                temas claro/oscuro y hoja de estilos
    ├── dialogos.py             login y configuración inicial
    ├── ventana_principal.py    Main: pestañas, permisos, tema, respaldo, cerrar sesión
    ├── widgets/                CrudTab, BarChart, KpiCard
    └── tabs/                   resumen, admin, editor_datos, usuarios, auditoria,
                                mi_cuenta, modulos (definición de Clientes/Ingresos/Egresos/Personal)
```

## Dónde tocar cuando…

| Quiero…                                         | Edito                                   |
|-------------------------------------------------|-----------------------------------------|
| Añadir una cuenta, tipo de ingreso/egreso o rol | `config.py`                             |
| Cambiar qué puede hacer cada rol                | `config.py` → `PERMISOS_USUARIO`        |
| Añadir un campo a Clientes/Ingresos/…           | `db/esquema.py` (tabla + migración) y `ui/tabs/modulos.py` |
| Cambiar un cálculo del resumen                  | `servicios/resumen.py`                  |
| Cambiar el Excel o el PDF                       | `servicios/exportacion.py`              |
| Cambiar colores o estilos                       | `ui/temas.py`                           |
| Añadir una pestaña nueva                        | crear `ui/tabs/<nombre>.py` y registrarla en `ui/ventana_principal.py` |

Regla de dependencias: `ui` puede importar de `servicios` y `db`; `servicios` puede importar de `db`; `db` y `servicios` no importan nada de `ui`.
