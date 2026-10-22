"""Configuración de la aplicación y validación de variables de entorno.

Las variables de entorno soportadas son exclusivamente las definidas en la
especificación del proyecto:

* ``DATABASE_URL``: cadena de conexión a PostgreSQL.
* ``SECRET_KEY``: clave de firma de los tokens JWT.
* ``ALGORITHM``: algoritmo de firma de los tokens JWT.
* ``ACCESS_TOKEN_EXPIRE_MINUTES``: vigencia del token de acceso en minutos.
* ``POSTGRES_USER``, ``POSTGRES_PASSWORD``, ``POSTGRES_DB``: credenciales de la base de datos.
* ``BACKEND_URL``, ``FRONTEND_URL``: URLs de los servicios (CORS y trazabilidad).

El módulo expone la instancia única ``settings``, construida a partir del
entorno, y ``validate_startup()``, que aborta el arranque cuando faltan las
variables obligatorias.
"""

from __future__ import annotations

import hashlib
import os
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app import __version__
from backend.app.core.exceptions import ConfigurationException

REQUIRED_ENV_VARS = ("DATABASE_URL", "SECRET_KEY")
"""Variables de entorno obligatorias para el arranque del servicio."""


class Settings(BaseModel):
    """Configuración de la aplicación resuelta desde el entorno."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    APP_NAME: str = Field(
        default="Pre-screening para Ensayos Clínicos Estado 1",
        description="Nombre del proyecto",
    )
    APP_VERSION: str = Field(default=__version__, description="Versión de la aplicación")
    SERVICE_NAME: str = Field(
        default="backend-service",
        description="Nombre del servicio publicado en el health check",
    )
    API_TITLE: str = Field(
        default="Motor de Pre-selección Clínica Inteligente",
        description="Título de la API",
    )

    SECRET_KEY: Optional[str] = Field(
        default=None,
        description="Clave de firma de los tokens JWT",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo de firma de los tokens JWT",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        description="Vigencia del token de acceso en minutos",
    )

    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Cadena de conexión a PostgreSQL",
    )
    POSTGRES_USER: str = Field(
        default="user",
        description="Usuario de PostgreSQL",
    )
    POSTGRES_PASSWORD: Optional[str] = Field(
        default=None,
        description="Contraseña de PostgreSQL",
    )
    POSTGRES_DB: str = Field(
        default="clinical_screening_db",
        description="Base de datos de PostgreSQL",
    )

    BACKEND_URL: str = Field(
        default="http://localhost:21001",
        description="URL pública del backend",
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:21000",
        description="URL pública del frontend",
    )

    @classmethod
    def from_env(cls) -> "Settings":
        """Construye la configuración leyendo las variables de entorno soportadas."""
        return cls(
            SECRET_KEY=_optional_env("SECRET_KEY"),
            ALGORITHM=_optional_env("ALGORITHM") or "HS256",
            ACCESS_TOKEN_EXPIRE_MINUTES=_positive_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30),
            DATABASE_URL=_optional_env("DATABASE_URL"),
            POSTGRES_USER=_optional_env("POSTGRES_USER") or "user",
            POSTGRES_PASSWORD=_optional_env("POSTGRES_PASSWORD"),
            POSTGRES_DB=_optional_env("POSTGRES_DB") or "clinical_screening_db",
            BACKEND_URL=_optional_env("BACKEND_URL") or "http://localhost:21001",
            FRONTEND_URL=_optional_env("FRONTEND_URL") or "http://localhost:21000",
        )

    def missing_required_env(self) -> List[str]:
        """Devuelve el nombre de las variables de entorno obligatorias ausentes."""
        missing = [
            name
            for name in REQUIRED_ENV_VARS
            if not getattr(self, name, None)
        ]
        return missing

    def validate_startup(self) -> "Settings":
        """Valida la configuración obligatoria y devuelve la instancia validada.

        Lanza `ConfigurationException` cuando falta alguna variable obligatoria,
        de modo que el proceso del backend no arranque con una configuración
        incompleta.
        """
        missing = self.missing_required_env()
        if missing:
            raise ConfigurationException(
                "Faltan variables de entorno obligatorias: " + ", ".join(missing)
            )
        return self

    @property
    def cors_origins(self) -> List[str]:
        """Orígenes permitidos para CORS, derivados de las URLs configuradas."""
        origins = [self.FRONTEND_URL, self.BACKEND_URL]
        return [origin for origin in origins if origin]

    @property
    def pii_encryption_key(self) -> Optional[str]:
        """Clave derivada de `SECRET_KEY` para cifrar campos de PII en la base de datos.

        No es una variable de entorno propia: se deriva de la clave de firma
        mediante SHA-256 para que exista una única fuente de secreto en el
        despliegue.
        """
        if not self.SECRET_KEY:
            return None
        return hashlib.sha256(self.SECRET_KEY.encode("utf-8")).hexdigest()


def _optional_env(name: str) -> Optional[str]:
    """Lee una variable de entorno devolviendo `None` si no existe o está vacía."""
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _positive_int_env(name: str, default: int) -> int:
    """Lee una variable de entorno entera y positiva, con valor por defecto."""
    raw = _optional_env(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationException(
            f"La variable de entorno {name} debe ser un número entero"
        ) from exc
    if value <= 0:
        raise ConfigurationException(
            f"La variable de entorno {name} debe ser un valor mayor que cero"
        )
    return value


def get_settings() -> Settings:
    """Construye una configuración nueva a partir del entorno actual."""
    return Settings.from_env()


def validate_startup() -> Settings:
    """Valida la configuración del entorno y devuelve la instancia validada."""
    return settings.validate_startup()


settings: Settings = get_settings()
"""Instancia única de configuración compartida por toda la aplicación."""


__all__ = [
    "REQUIRED_ENV_VARS",
    "Settings",
    "get_settings",
    "settings",
    "validate_startup",
]
