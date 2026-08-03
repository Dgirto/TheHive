"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_THEHIVE_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_THEHIVE_"


@dataclass(frozen=True)
class TheHiveConfig:
    """Parámetros de conexión a TheHive."""

    base_url: str
    api_key: str
    connect_timeout: int = 15

    @classmethod
    def from_env(cls) -> TheHiveConfig:
        """Construye la configuración desde las variables RUVIC_THEHIVE_*.

        Raises:
            ValueError: si falta alguna variable obligatoria.

        Ejemplo:
            >>> config = TheHiveConfig.from_env()
            >>> config.base_url
            'https://thehive.empresa.com'
        """
        missing = [
            f"{ENV_PREFIX}{name}"
            for name in ("BASE_URL", "API_KEY")
            if not os.environ.get(f"{ENV_PREFIX}{name}")
        ]
        if missing:
            raise ValueError(
                "Faltan variables de entorno del conector thehive: "
                + ", ".join(missing)
                + ". Configura el conector en Settings → Conectores."
            )
        return cls(
            base_url=os.environ[f"{ENV_PREFIX}BASE_URL"].rstrip("/"),
            api_key=os.environ[f"{ENV_PREFIX}API_KEY"],
            connect_timeout=int(os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT", "15")),
        )
