---
name: thehive
description: >
  Usa la librería ruvic_thehive_connector para gestionar casos e
  incidentes de seguridad en TheHive - crear un caso (create_case),
  agregar una tarea a un caso (add_task), actualizar el estado de un
  caso (update_case_status), y agregar un observable/IOC a un caso
  (add_observable). Úsala cuando el usuario pida registrar, dar
  seguimiento o escalar un incidente de seguridad.
triggers:
- thehive
- caso de seguridad
- incidente de seguridad
- observable
- ioc
---

# Conector TheHive (ruvic_thehive_connector)

Librería Python de gestión de casos para TheHive. Está **preinstalada en el runtime** cuando el conector está configurado (si no, instálala con `pip install git+https://github.com/Dgirto/TheHive.git#subdirectory=lib`).

## Regla crítica de credenciales

El código generado **NUNCA hardcodea credenciales**. Siempre se leen de variables de entorno, disponibles cuando el conector `thehive` está configurado:

| Variable | Contenido |
|----------|-----------|
| `RUVIC_THEHIVE_BASE_URL` | URL base de la instancia de TheHive |
| `RUVIC_THEHIVE_API_KEY` | API Key del usuario de servicio |
| `RUVIC_THEHIVE_CONNECT_TIMEOUT` | (opcional) timeout en segundos |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en **Settings → Conectores**.

## Este conector SÍ escribe

A diferencia de los conectores de solo consulta, `thehive` crea y modifica casos reales en la plataforma de gestión de incidentes. Confirma con el usuario antes de crear un caso o cambiar su estado si la acción no fue explícitamente solicitada.

## Conexión (siempre igual)

```python
from ruvic_thehive_connector import TheHiveClient

client = TheHiveClient()  # lee RUVIC_THEHIVE_* del entorno automáticamente
```

## Capacidad 1 — Crear un caso

```python
case = client.create_case(
    title="Phishing sospechoso reportado por usuario",
    description="Correo con enlace sospechoso recibido por finanzas@empresa.com",
    severity=3,  # 1=baja, 2=media, 3=alta, 4=crítica
    tlp=2,       # 0=blanco, 1=verde, 2=ámbar, 3=rojo
    tags=["phishing", "email"],
)
case_id = case["_id"]
```

## Capacidad 2 — Agregar una tarea al caso

```python
client.add_task(case_id, "Analizar cabeceras del correo", description="Revisar SPF/DKIM/DMARC")
```

## Capacidad 3 — Actualizar el estado del caso

```python
client.update_case_status(case_id, "InProgress")
```

Estados válidos: `New`, `InProgress`, `Indeterminate`, `FalsePositive`, `TruePositive`, `Other`.

## Capacidad 4 — Agregar un observable (IOC)

```python
client.add_observable(case_id, "ip", "45.33.22.11", message="IP de origen del correo", ioc=True)
```

Tipos de dato comunes: `ip`, `domain`, `hash`, `mail`, `url`, `filename`.

## Manejo de errores

```python
from ruvic_thehive_connector import (
    TheHiveAuthError, TheHiveDataError, TheHiveNetworkError,
)

try:
    client.update_case_status(case_id, "InProgress")
except TheHiveAuthError:
    print("Credenciales inválidas o sin permiso suficiente")
except TheHiveNetworkError:
    print("No se pudo alcanzar TheHive — reintenta en unos segundos")
except TheHiveDataError as e:
    print(f"Error de datos: {e}")  # ej. el caso no existe o el estado es inválido
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de las variables `RUVIC_THEHIVE_*` (el constructor de `TheHiveClient` ya lo hace).
2. Nunca imprimas `RUVIC_THEHIVE_API_KEY` en logs ni en la salida.
3. Este conector modifica datos reales: no crees casos ni cambies estados sin que el usuario lo haya pedido explícitamente.
4. Guarda siempre el `_id` retornado por `create_case` — se necesita para `add_task`, `update_case_status` y `add_observable` posteriores.
5. Usa severidades y TLP conservadores (no marques todo como crítico/rojo) salvo que el usuario indique lo contrario.
