"""Prueba de conexión estándar del conector thehive.

Firma estándar Ruvic: def test_connection() -> tuple[bool, str]
- Lee la configuración EXCLUSIVAMENTE de las env vars RUVIC_THEHIVE_*.
- Nunca lanza excepciones; retorna (ok, mensaje).

Ejecutable también como script para pruebas locales:
    python test_connection.py
"""

from __future__ import annotations


def test_connection() -> tuple[bool, str]:
    """Conecta a TheHive y consulta el usuario autenticado usando las env
    vars RUVIC_THEHIVE_*."""
    try:
        from ruvic_thehive_connector import (
            TheHiveAuthError,
            TheHiveClient,
            TheHiveDataError,
            TheHiveNetworkError,
        )
    except ImportError:
        return (
            False,
            "La librería ruvic-thehive-connector no está instalada. "
            "Instala con: pip install git+https://github.com/Dgirto/"
            "TheHive.git#subdirectory=lib",
        )

    try:
        client = TheHiveClient()  # valida que existan las env vars
    except ValueError as exc:
        return False, str(exc)

    try:
        client.ping()
    except TheHiveAuthError as exc:
        return False, f"Autenticación fallida: {exc}"
    except TheHiveNetworkError as exc:
        return False, f"Error de red: {exc}"
    except TheHiveDataError as exc:
        return False, f"Error de datos: {exc}"
    except Exception as exc:  # red de seguridad: jamás propagar
        return False, f"Error inesperado: {exc}"

    return (
        True,
        f"Conexión exitosa a TheHive ({client.config.base_url})",
    )


if __name__ == "__main__":
    ok, message = test_connection()
    print(f"{'OK' if ok else 'FALLO'}: {message}")
    raise SystemExit(0 if ok else 1)
