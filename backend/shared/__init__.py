"""Módulos compartidos entre el backend y el frontend.

El paquete expone los contratos de datos y las dependencias de la API:

* :mod:`backend.shared.schemas`: modelos Pydantic de la API.
* :mod:`backend.shared.dependencies`: dependencias FastAPI de autenticación y
  roles.

Las utilidades de enmascarado de PII y de hash encadenado residen en
``backend.shared.utils``.
"""

from backend.shared.dependencies import (
    get_current_active_gestor,
    get_current_active_investigador,
    get_current_active_user,
)
from backend.shared.schemas import (
    AuditLogBase,
    AuditLogResponse,
    BaseSchema,
    CondicionMedicaBase,
    CondicionMedicaCreate,
    CondicionMedicaResponse,
    CriterioBase,
    CriterioResponse,
    EvaluationMetrics,
    EvaluacionBase,
    EvaluacionCreate,
    EvaluacionResponse,
    EvaluacionSubmitData,
    LoginRequest,
    MedicacionBase,
    MedicacionCreate,
    MedicacionResponse,
    PacienteBase,
    PacienteCreate,
    PacienteResponse,
    PacienteUpdate,
    ProtocoloBase,
    ProtocoloResponse,
    ReglaEvaluacionBase,
    ReglaEvaluacionResponse,
    Token,
    TokenData,
    UsuarioBase,
    UsuarioCreate,
    UsuarioResponse,
)

__all__ = [
    "AuditLogBase",
    "AuditLogResponse",
    "BaseSchema",
    "CondicionMedicaBase",
    "CondicionMedicaCreate",
    "CondicionMedicaResponse",
    "CriterioBase",
    "CriterioResponse",
    "EvaluationMetrics",
    "EvaluacionBase",
    "EvaluacionCreate",
    "EvaluacionResponse",
    "EvaluacionSubmitData",
    "LoginRequest",
    "MedicacionBase",
    "MedicacionCreate",
    "MedicacionResponse",
    "PacienteBase",
    "PacienteCreate",
    "PacienteResponse",
    "PacienteUpdate",
    "ProtocoloBase",
    "ProtocoloResponse",
    "ReglaEvaluacionBase",
    "ReglaEvaluacionResponse",
    "Token",
    "TokenData",
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioResponse",
    "get_current_active_gestor",
    "get_current_active_investigador",
    "get_current_active_user",
]
