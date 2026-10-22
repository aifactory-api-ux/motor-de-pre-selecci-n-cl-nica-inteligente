"""Esquemas Pydantic que definen los contratos de datos de la API.

Los nombres, campos y valores de enumeración reproducen exactamente el
contrato de datos de la especificación (§2) y el contrato de la API
(`api_contract.yaml`), de forma que el frontend TypeScript y el backend
Python compartan una única definición de la interfaz.

Todos los esquemas de respuesta declaran ``from_attributes`` para poder
serializar directamente instancias de los modelos ORM.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.database.models import generate_uuid7

RolUsuario = Literal["investigador", "gestor"]
"""Roles de usuario admitidos por la API."""

TipoCriterio = Literal["inclusion", "exclusion"]
"""Naturaleza admitida para un criterio de protocolo."""

ResultadoEvaluacion = Literal["elegible", "noElegible", "pendiente"]
"""Veredictos admitidos para una evaluación."""

EstadoEvaluacion = Literal["pendiente", "completada", "en_revision"]
"""Estados admitidos en el ciclo de vida de una evaluación."""


class BaseSchema(BaseModel):
    """Base común con identificador único generado por defecto.

    El identificador se genera como UUID v7 (RFC 9562) mediante
    `generate_uuid7`, la misma estrategia que aplican los modelos ORM de
    `backend.database.models`. De este modo, los identificadores emitidos por
    la API y los persistidos en PostgreSQL son ordenables por tiempo y
    verificables.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=generate_uuid7)


# --- USUARIO ---
class UsuarioBase(BaseModel):
    """Datos comunes de un usuario del sistema."""

    nombre: str
    email: str
    rol: RolUsuario
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    """Alta de usuario; la contraseña viaja en texto plano por HTTPS."""

    password: str


class UsuarioResponse(UsuarioBase):
    """Usuario devuelto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- PACIENTE ---
class PacienteBase(BaseModel):
    """Datos comunes de un paciente evaluable."""

    codigo_interno: str = Field(
        description="Código interno enmascarado del paciente"
    )
    seudonimo: str = Field(description="Seudónimo del paciente, enmascarado")
    fecha_nacimiento: date
    genero: str
    datos_clinicos: str = Field(
        description="Datos clínicos relevantes, enmascarados o anonimizados"
    )


class PacienteCreate(PacienteBase):
    """Alta de paciente en el sistema."""


class PacienteUpdate(PacienteBase):
    """Actualización de los datos de un paciente."""


class PacienteResponse(PacienteBase):
    """Paciente devuelto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- PROTOCOLO ---
class ProtocoloBase(BaseModel):
    """Datos comunes de un protocolo clínico."""

    nombre: str
    version: str
    fecha_vigencia: date
    descripcion: str


class ProtocoloResponse(ProtocoloBase):
    """Protocolo devuelto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- CRITERIO ---
class CriterioBase(BaseModel):
    """Criterio de inclusión o exclusión asociado a un protocolo."""

    protocolo_id: UUID
    tipo: TipoCriterio
    codigo: str
    descripcion: str
    umbral: str = Field(description="Regla aplicada, por ejemplo 'edad >= 18'")


class CriterioResponse(CriterioBase):
    """Criterio devuelto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- MEDICACION ---
class MedicacionBase(BaseModel):
    """Medicación registrada para un paciente."""

    paciente_id: UUID
    nombre: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    tipo: str


class MedicacionCreate(MedicacionBase):
    """Alta de medicación de un paciente."""


class MedicacionResponse(MedicacionBase):
    """Medicación devuelta por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- CONDICION_MEDICA ---
class CondicionMedicaBase(BaseModel):
    """Antecedente clínico de un paciente."""

    paciente_id: UUID
    diagnostico: str
    fecha_diagnostico: date
    detalle: str


class CondicionMedicaCreate(CondicionMedicaBase):
    """Alta de antecedente clínico de un paciente."""


class CondicionMedicaResponse(CondicionMedicaBase):
    """Antecedente clínico devuelto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- EVALUACION ---
class EvaluacionBase(BaseModel):
    """Datos comunes de una evaluación de pre-selección."""

    paciente_id: UUID
    usuario_id: UUID
    protocolo_id: UUID
    fecha_evaluacion: date
    resultado: Optional[ResultadoEvaluacion] = None
    estado: EstadoEvaluacion = Field(default="pendiente")


class EvaluacionCreate(BaseModel):
    """Solicitud de inicio de una evaluación."""

    paciente_id: UUID
    protocolo_id: UUID


class EvaluacionSubmitData(BaseModel):
    """Datos clínicos del paciente enviados para aplicar el protocolo.

    Los rangos validan la coherencia clínica antes de evaluar: la edad es
    humana, las escalas PASI y BSA son porcentajes y la cronicidad se
    expresa en meses.
    """

    edad: int = Field(ge=0, le=120)
    pasi_score: float = Field(ge=0, le=100)
    bsa_score: float = Field(ge=0, le=100)
    psoriasis_cronica_meses: int = Field(ge=0, le=1200)
    historial_tb: bool
    embarazo: bool
    biologicos_corticoides_recientes: bool


class EvaluacionResponse(EvaluacionBase):
    """Evaluación devuelta por la API, con su contexto relacionado."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    paciente: PacienteResponse
    protocolo: ProtocoloResponse
    usuario: UsuarioResponse


# --- REGLA_EVALUACION ---
class ReglaEvaluacionBase(BaseModel):
    """Detalle de la evaluación de un criterio concreto."""

    evaluacion_id: UUID
    criterio_id: UUID
    cumple: bool
    motivo_rechazo: Optional[str] = None
    valor_paciente: Optional[str] = None
    umbral_evaluado: Optional[str] = None


class ReglaEvaluacionResponse(ReglaEvaluacionBase):
    """Regla evaluada devuelta por la API, con el detalle del criterio."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    criterio: CriterioResponse


# --- AUDIT_LOG ---
class AuditLogBase(BaseModel):
    """Entrada inmutable del registro de auditoría."""

    evaluacion_id: UUID
    usuario_id: UUID
    fecha_registro: date
    regla_rechazo: Optional[str] = None
    detalle: str
    hash_encadenado: str = Field(
        description="Hash encadenado para inmutabilidad GxP"
    )


class AuditLogResponse(AuditLogBase):
    """Entrada de auditoría devuelta por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


# --- AUTENTICACIÓN ---
class LoginRequest(BaseModel):
    """Credenciales de acceso al servicio."""

    email: str
    password: str


class Token(BaseModel):
    """Token de acceso emitido tras una autenticación correcta."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Contenido mínimo del token decodificado."""

    email: Optional[str] = None


# --- MÉTRICAS ---
class EvaluationMetrics(BaseModel):
    """Indicadores de actividad del panel de reclutamiento."""

    total_evaluaciones: int
    elegibles: int
    no_elegibles: int
    pendientes: int
    motivos_rechazo_top: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Motivos de rechazo más frecuentes, por ejemplo [{'motivo': 'Edad', 'count': 10}]",
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
    "EstadoEvaluacion",
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
    "ResultadoEvaluacion",
    "RolUsuario",
    "Token",
    "TokenData",
    "TipoCriterio",
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioResponse",
]
