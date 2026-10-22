"""Gestión del motor, de la sesión y del esquema de la base de datos.

El módulo centraliza el acceso a PostgreSQL:

* ``Base``: base declarativa compartida por todos los modelos ORM.
* ``get_engine()`` / ``get_session_factory()``: motor y fábrica de sesiones
  creados de forma diferida, de modo que importar el módulo nunca falle por
  ausencia de configuración en el entorno.
* ``get_db()``: dependencia de FastAPI que entrega una sesión por petición.
* ``session_scope()``: gestor de contexto con commit automático.
* ``init_db()`` / ``close_db()``: creación del esquema y liberación del pool.

La cadena de conexión se toma de ``DATABASE_URL`` y, si no está definida, se
compone con ``POSTGRES_USER``, ``POSTGRES_PASSWORD`` y ``POSTGRES_DB``, sin
introducir variables de entorno nuevas.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Iterator, Optional
from urllib.parse import quote_plus

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

POSTGRES_HOST_POR_DEFECTO = "db"
"""Host por defecto del servicio de base de datos en el despliegue Docker."""

POSTGRES_PUERTO_POR_DEFECTO = 5432
"""Puerto por defecto del servicio de base de datos."""


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos ORM del proyecto."""


_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def get_database_url() -> str:
    """Resuelve la cadena de conexión a PostgreSQL.

    Returns:
        Valor de ``DATABASE_URL`` si está configurado; en caso contrario se
        compone con las credenciales ``POSTGRES_*`` del entorno.
    """
    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    usuario = quote_plus(settings.POSTGRES_USER or "user")
    password = settings.POSTGRES_PASSWORD
    credenciales = (
        f"{usuario}:{quote_plus(password)}@" if password else f"{usuario}@"
    )
    base_datos = settings.POSTGRES_DB or "clinical_screening_db"
    return (
        f"postgresql://{credenciales}"
        f"{POSTGRES_HOST_POR_DEFECTO}:{POSTGRES_PUERTO_POR_DEFECTO}/{base_datos}"
    )


def get_engine() -> Engine:
    """Devuelve el motor de SQLAlchemy, creándolo en el primer uso.

    Returns:
        Motor configurado con ``pool_pre_ping`` para tolerar conexiones
        caducas en entornos contenerizados.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            future=True,
        )
        logger.debug("Motor de base de datos inicializado")
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Devuelve la fábrica de sesiones, creándola en el primer uso.

    Returns:
        Fábrica ligada al motor activo. Las sesiones no caducan los objetos al
        confirmar, de modo que la respuesta de la API pueda serializarse sin
        provocar lecturas adicionales.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos a la aplicación.

    Es la dependencia de FastAPI utilizada por los routers: la sesión se abre
    al entrar en la petición, se confirma o revierte según el resultado de la
    operación y se cierra al finalizar.

    Yields:
        Sesión de SQLAlchemy activa durante la petición.
    """
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Gestor de contexto con confirmación automática y reversión ante errores.

    Yields:
        Sesión de SQLAlchemy que confirma al salir del bloque sin excepciones.
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Crea el esquema de la base de datos y activa las garantías del audit trail.

    Los modelos se importan de forma diferida para registrar los mappers en la
    base declarativa sin acoplar este módulo a la capa de modelos en tiempo de
    importación.
    """
    import backend.database.models  # noqa: F401 - registra los mappers

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    activar_inmutabilidad_audit_log(engine)
    logger.info("Esquema de base de datos verificado")


def activar_inmutabilidad_audit_log(engine: Optional[Engine] = None) -> None:
    """Instala el trigger de PostgreSQL que bloquea cambios en ``audit_log``.

    La garantía de inmutabilidad se aplica además de la implementada en la
    capa ORM, de modo que ninguna sentencia SQL pueda alterar el registro de
    auditoría, ni siquiera mediante operaciones masivas.

    Args:
        engine: Motor sobre el que se instala el trigger; por defecto el
            motor activo de la aplicación.
    """
    motor = engine or get_engine()
    if motor.dialect.name != "postgresql":
        logger.info(
            "El motor '%s' no soporta triggers: la inmutabilidad del audit trail "
            "queda garantizada únicamente en la capa ORM",
            motor.dialect.name,
        )
        return

    with motor.begin() as connection:
        connection.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION audit_log_bloquear_mutaciones() RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION 'AUDIT_LOG es inmutable: no se permiten modificaciones ni eliminaciones';
                END;
                $$ LANGUAGE plpgsql;
                """
            )
        )
        connection.execute(
            text("DROP TRIGGER IF EXISTS trg_audit_log_inmutable ON audit_log")
        )
        connection.execute(
            text(
                """
                CREATE TRIGGER trg_audit_log_inmutable
                BEFORE UPDATE OR DELETE ON audit_log
                FOR EACH ROW EXECUTE FUNCTION audit_log_bloquear_mutaciones()
                """
            )
        )


def close_db() -> None:
    """Libera el motor y la fábrica de sesiones.

    Se invoca al apagar el servicio para devolver las conexiones al sistema.
    """
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
        logger.debug("Motor de base de datos liberado")
    _engine = None
    _session_factory = None


__all__ = [
    "Base",
    "activar_inmutabilidad_audit_log",
    "close_db",
    "get_database_url",
    "get_db",
    "get_engine",
    "get_session_factory",
    "init_db",
    "session_scope",
]
