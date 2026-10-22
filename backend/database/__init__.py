"""Capa de persistencia del servicio backend.

El paquete agrupa el acceso a la base de datos PostgreSQL:

* :mod:`backend.database.models`: modelos ORM que reflejan el ERD.
* :mod:`backend.database.session`: motor, sesión y creación del esquema.
* :mod:`backend.database.crud`: operaciones CRUD genéricas reutilizables.
"""

from backend.database.crud import (
    CRUDBase,
    audit_log_crud,
    criterio_crud,
    condicion_medica_crud,
    evaluacion_crud,
    medicacion_crud,
    paciente_crud,
    protocolo_crud,
    regla_evaluacion_crud,
    usuario_crud,
)
from backend.database.models import (
    AuditLog,
    CondicionMedica,
    Criterio,
    Evaluacion,
    Medicacion,
    Paciente,
    Protocolo,
    ReglaEvaluacion,
    Usuario,
)
from backend.database.session import (
    Base,
    close_db,
    get_db,
    get_engine,
    get_session_factory,
    init_db,
    session_scope,
)

__all__ = [
    "AuditLog",
    "Base",
    "CRUDBase",
    "CondicionMedica",
    "Criterio",
    "Evaluacion",
    "Medicacion",
    "Paciente",
    "Protocolo",
    "ReglaEvaluacion",
    "Usuario",
    "audit_log_crud",
    "close_db",
    "criterio_crud",
    "condicion_medica_crud",
    "evaluacion_crud",
    "get_db",
    "get_engine",
    "get_session_factory",
    "init_db",
    "medicacion_crud",
    "paciente_crud",
    "protocolo_crud",
    "regla_evaluacion_crud",
    "session_scope",
    "usuario_crud",
]
