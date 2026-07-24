# Conector TheHive (CON-050)

Conector Ruvic de gestión de casos e incidentes de seguridad para
TheHive (API v1). Permite crear un caso, agregar una tarea, actualizar
el estado de un caso, y agregar un observable (IOC).

## Instalación

```bash
pip install git+https://github.com/Dgirto/TheHive.git#subdirectory=lib
```

Python 3.10+. Dependencia única: `requests>=2.31,<3.0`.

## Permisos requeridos en TheHive

Crea un usuario de servicio dedicado en la organización correspondiente,
con un perfil que otorgue únicamente:

- `manageCase`: crear casos y actualizar su estado.
- `manageTask`: agregar tareas a un caso.
- `manageObservable`: agregar observables a un caso.

No otorgues perfiles con `manageOrganisation`, `manageUser` ni
`manageConfig` — el conector no necesita administrar la plataforma.
Genera la API Key desde el perfil del usuario de servicio en TheHive
(icono de usuario → "My profile" → "API Key" → "Create").

## Variables de entorno (`RUVIC_THEHIVE_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_THEHIVE_BASE_URL` | Sí | URL base de la instancia (ej. `https://thehive.empresa.com`) |
| `RUVIC_THEHIVE_API_KEY` | Sí | API Key del usuario de servicio |
| `RUVIC_THEHIVE_CONNECT_TIMEOUT` | No (default `15`) | Timeout de conexión en segundos |

## Pruebas locales

Con Docker (instancia de prueba con Cassandra + Elasticsearch embebidos
vía la imagen oficial, o una instancia TheHive existente):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_THEHIVE_BASE_URL=https://tu-instancia-thehive.com
export RUVIC_THEHIVE_API_KEY=tu-api-key

python test_connection.py
python validate_local.py
```

Prueba también los casos de error (API Key inválida, caso inexistente,
estado inválido) y verifica que los mensajes sean claros.

## Notas de integración

- Este conector **SÍ escribe**: crea casos, tareas y observables reales
  en TheHive. No es de solo lectura.
- `update_case_status` valida a nivel de código que el estado sea uno de
  los valores permitidos por TheHive (`New`, `InProgress`,
  `Indeterminate`, `FalsePositive`, `TruePositive`, `Other`) antes de
  enviar la petición.
- `create_case` retorna el `_id` del caso creado, necesario para
  `add_task`, `update_case_status` y `add_observable` posteriores sobre
  el mismo caso.
- Los tipos de observable (`data_type`) deben coincidir con los tipos
  configurados en la instancia de TheHive (por defecto incluye `ip`,
  `domain`, `hash`, `mail`, `url`, `filename`, entre otros).
