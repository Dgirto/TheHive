"""Validación local del conector thehive: ejercita las 4 capacidades.

Uso:
    python validate_local.py

Requiere las variables RUVIC_THEHIVE_* exportadas en el entorno, con un
usuario de servicio con permisos manageCase/manageTask/manageObservable.
"""

from ruvic_thehive_connector import TheHiveClient, setup_logging

setup_logging("INFO")
client = TheHiveClient()

print("== 1. Crear caso ==")
case = client.create_case(
    "Caso de prueba validate_local.py",
    "Caso creado automáticamente para validar el conector Ruvic",
    severity=1,
    tlp=1,
    tags=["ruvic-test"],
)
case_id = case["_id"]
print(f"  case_id={case_id}")

print("== 2. Agregar tarea ==")
task = client.add_task(case_id, "Tarea de prueba", description="Verificar el conector")
print(f"  task_id={task.get('_id')}")

print("== 3. Actualizar estado del caso ==")
updated = client.update_case_status(case_id, "InProgress")
print(f"  status={updated.get('status')}")

print("== 4. Agregar observable ==")
observable = client.add_observable(case_id, "ip", "203.0.113.10", message="IP de prueba", ioc=False)
print(f"  observable_id={observable.get('_id')}")

print("\nTodo OK: create_case, add_task, update_case_status y add_observable funcionan.")
