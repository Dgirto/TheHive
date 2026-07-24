"""Excepciones propias del conector TheHive.

Separan los tres tipos de fallo que el usuario debe distinguir:
autenticación, red/servidor y datos. Nunca exponemos excepciones
crípticas del cliente HTTP subyacente.
"""


class TheHiveConnectorError(Exception):
    """Error base del conector."""


class TheHiveAuthError(TheHiveConnectorError):
    """Credenciales inválidas o permisos insuficientes."""


class TheHiveNetworkError(TheHiveConnectorError):
    """No se pudo alcanzar la instancia de TheHive (red/timeout)."""


class TheHiveDataError(TheHiveConnectorError):
    """La operación es válida pero el caso/tarea/observable es inválido."""
