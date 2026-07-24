"""Cliente de gestión de casos e incidentes para TheHive (API v1).

Capacidades:
- create_case():          crear un nuevo caso.
- add_task():              agregar una tarea a un caso.
- update_case_status():    actualizar el estado de un caso.
- add_observable():        agregar un observable (IOC) a un caso.

Las credenciales SIEMPRE provienen de variables de entorno RUVIC_THEHIVE_*
(ver config.TheHiveConfig.from_env). Prohibido hardcodearlas.
"""

from __future__ import annotations

from typing import Any

import requests

from .config import TheHiveConfig
from .exceptions import TheHiveAuthError, TheHiveDataError, TheHiveNetworkError
from .logging_utils import get_logger

_VALID_STATUSES = {"New", "InProgress", "Indeterminate", "FalsePositive", "TruePositive", "Other"}


class TheHiveClient:
    """Cliente de gestión de casos e incidentes de seguridad en TheHive.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_THEHIVE_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = TheHiveClient()  # lee RUVIC_THEHIVE_* del entorno
        >>> client.create_case("Phishing sospechoso", "Reportado por usuario")
        {'id': '~12345', 'title': 'Phishing sospechoso', ...}
    """

    def __init__(self, config: TheHiveConfig | None = None) -> None:
        self.config = config or TheHiveConfig.from_env()
        self._logger = get_logger()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.config.base_url}{path}"
        try:
            response = self._session.request(
                method, url, timeout=self.config.connect_timeout, **kwargs
            )
        except requests.exceptions.RequestException as exc:
            raise TheHiveNetworkError(
                f"No se pudo alcanzar TheHive en {self.config.base_url!r}: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            raise TheHiveAuthError(
                "Credenciales inválidas o sin permiso suficiente para esta operación."
            )
        if response.status_code >= 400:
            raise TheHiveDataError(
                f"TheHive respondió {response.status_code}: {response.text[:300]}"
            )
        return response.json() if response.content else None

    def ping(self) -> bool:
        """Verifica la conexión consultando el usuario autenticado actual.

        Returns:
            True si la conexión funciona.

        Raises:
            TheHiveAuthError / TheHiveNetworkError / TheHiveDataError según
            el fallo.
        """
        self._request("GET", "/api/v1/user/current")
        self._logger.info("Ping exitoso a TheHive %s", self.config.base_url)
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: crear caso
    # ------------------------------------------------------------------ #

    def create_case(
        self,
        title: str,
        description: str,
        severity: int = 2,
        tlp: int = 2,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Crea un nuevo caso.

        Args:
            title: título del caso.
            description: descripción del caso.
            severity: severidad 1 (baja) a 4 (crítica). Default 2.
            tlp: Traffic Light Protocol, 0 (blanco) a 3 (rojo). Default 2 (verde).
            tags: lista opcional de etiquetas.

        Returns:
            Dict con el caso creado (incluye "id" y "_id").

        Ejemplo:
            >>> client.create_case("Phishing sospechoso", "Reportado por usuario")
            {'id': '~12345', 'title': 'Phishing sospechoso', ...}
        """
        title = (title or "").strip()
        if not title:
            raise TheHiveDataError("title no puede estar vacío.")
        body = {
            "title": title,
            "description": description or "",
            "severity": severity,
            "tlp": tlp,
            "tags": tags or [],
        }
        result = self._request("POST", "/api/v1/case", json=body)
        self._logger.info('Caso creado: "%s" (id=%s)', title, result.get("_id"))
        return result

    # ------------------------------------------------------------------ #
    # Capacidad 2: agregar tarea a un caso
    # ------------------------------------------------------------------ #

    def add_task(self, case_id: str, title: str, description: str = "") -> dict[str, Any]:
        """Agrega una tarea a un caso existente.

        Args:
            case_id: ID del caso (`_id` retornado por create_case).
            title: título de la tarea.
            description: descripción opcional.

        Returns:
            Dict con la tarea creada.

        Ejemplo:
            >>> client.add_task("~12345", "Analizar cabeceras del correo")
            {'_id': '~67890', 'title': 'Analizar cabeceras del correo', ...}
        """
        case_id = (case_id or "").strip()
        title = (title or "").strip()
        if not case_id or not title:
            raise TheHiveDataError("case_id y title no pueden estar vacíos.")
        body = {"title": title, "description": description or ""}
        result = self._request("POST", f"/api/v1/case/{case_id}/task", json=body)
        self._logger.info('Tarea agregada a caso %s: "%s"', case_id, title)
        return result

    # ------------------------------------------------------------------ #
    # Capacidad 3: actualizar estado de un caso
    # ------------------------------------------------------------------ #

    def update_case_status(self, case_id: str, status: str) -> dict[str, Any]:
        """Actualiza el estado de un caso.

        Args:
            case_id: ID del caso.
            status: uno de New, InProgress, Indeterminate, FalsePositive,
                TruePositive, Other.

        Returns:
            Dict con el caso actualizado.

        Ejemplo:
            >>> client.update_case_status("~12345", "InProgress")
            {'_id': '~12345', 'status': 'InProgress', ...}
        """
        case_id = (case_id or "").strip()
        if not case_id:
            raise TheHiveDataError("case_id no puede estar vacío.")
        if status not in _VALID_STATUSES:
            raise TheHiveDataError(
                f"status {status!r} inválido. Valores permitidos: {sorted(_VALID_STATUSES)}"
            )
        result = self._request("PATCH", f"/api/v1/case/{case_id}", json={"status": status})
        self._logger.info("Caso %s actualizado a estado %s", case_id, status)
        return result

    # ------------------------------------------------------------------ #
    # Capacidad 4: agregar observable a un caso
    # ------------------------------------------------------------------ #

    def add_observable(
        self,
        case_id: str,
        data_type: str,
        data: str,
        message: str = "",
        ioc: bool = False,
    ) -> dict[str, Any]:
        """Agrega un observable (IOC) a un caso.

        Args:
            case_id: ID del caso.
            data_type: tipo de dato (ej. "ip", "domain", "hash", "mail").
            data: valor del observable (ej. "1.2.3.4").
            message: descripción opcional.
            ioc: marca el observable como indicador de compromiso.

        Returns:
            Dict con el observable creado.

        Ejemplo:
            >>> client.add_observable("~12345", "ip", "1.2.3.4", ioc=True)
            {'_id': '~11111', 'dataType': 'ip', 'data': '1.2.3.4', ...}
        """
        case_id = (case_id or "").strip()
        data_type = (data_type or "").strip()
        data = (data or "").strip()
        if not case_id or not data_type or not data:
            raise TheHiveDataError("case_id, data_type y data no pueden estar vacíos.")
        body = {"dataType": data_type, "data": data, "message": message or "", "ioc": ioc}
        result = self._request("POST", f"/api/v1/case/{case_id}/observable", json=body)
        self._logger.info('Observable agregado a caso %s: %s="%s"', case_id, data_type, data)
        return result
