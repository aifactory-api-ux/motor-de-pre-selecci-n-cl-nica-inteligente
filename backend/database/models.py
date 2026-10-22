"""Modelos ORM (SQLAlchemy 2.0) que reflejan el ERD del proyecto.

Cada entidad de la especificación tiene su clase equivalente:

===================  =====================  ==========================
Entidad (ERD)       Clase ORM              Tabla
===================  =====================  ==========================
``USUARIO``         :class:`Usuario`       ``usuario``
``PACIENTE``        :class:`Paciente`      ``paciente``
``PROTOCOLO``       :class:`Protocolo`     ``protocolo``
``CRITERIO``        :class:`Criterio`      ``criterio``
``MEDICACION``      :class:`Medicacion`    ``medicacion``
``CONDICION_MEDICA`` :class:`CondicionMedica` ``condicion_medica``
``EVALUACION``      :class:`Evaluacion`    ``evaluacion``
``REGLA_EVALUACION`` :class:`ReglaEvaluacion` ``regla_evaluacion``
``AUDIT_LOG``       :class:`AuditLog`      ``audit_log``
===================  =====================  ==========================

Además de traducir el ERD, el módulo aplica dos garantías exigidas por la
normativa clínica (GDPR/HIPAA y GxP):

1. Los identificadores son UUID v7, ordenables por tiempo, de modo que el
   encadenado de hashes del audit trail sea determinista y reproducible.
2. ``audit_log`` es inmutable (no admite actualizaciones ni borrados) y los
   pacientes ya evaluados no admiten alteraciones clínicas: para ellos sólo
   se permite el borrado lógico mediante ``activo = False``.
3. Las colecciones se configuran con ``passive_deletes=True``: el ORM no anula
   las claves foráneas de los hijos al eliminar un padre, de modo que la
   integridad la impone la base de datos (``ON DELETE CASCADE`` en las tablas
   clínicas y ``RESTRICT`` en las que forman parte del audit trail).
"""

import secrets
import time
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    event,
    inspect,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.app.core.exceptions import AppException
from backend.database.session import Base

ROLES_VALIDOS = ("investigador", "gestor")
"""Roles de usuario reconocidos por la API."""

TIPOS_CRITERIO_VALIDOS = ("inclusion", "exclusion")
"""Naturaleza admitida para un criterio de protocolo."""

RESULTADOS_EVALUACION_VALIDOS = ("elegible", "noElegible", "pendiente")
"""Veredictos admitidos para una evaluación."""

ESTADOS_EVALUACION_VALIDOS = ("pendiente", "completada", "en_revision")
"""Estados admitidos para el ciclo de vida de una evaluación."""


_ultimo_timestamp_ms = 0
"""Marca temporal del último UUID v7 generado, para garantizar monotonía."""

_ultimo_contador_aleatorio = 0
"""Parte aleatoria (74 bits) del último UUID v7 generado."""


def generate_uuid7() -> uuid.UUID:
    """Genera un UUID v7 (RFC 9562) ordenable por tiempo de creación.

    El identificador se compone de 48 bits de marca temporal en milisegundos,
    4 bits de versión, 12 bits aleatorios, 2 bits de variante y 62 bits
    aleatorios. La parte aleatoria actúa como contador dentro del mismo
    milisegundo, de modo que los identificadores generados son estrictamente
    crecientes. Así, el orden de inserción de los registros de auditoría es
    determinista y el hash encadenado puede recalcularse en cualquier momento.

    Returns:
        Identificador UUID v7.
    """
    global _ultimo_timestamp_ms, _ultimo_contador_aleatorio

    unix_ts_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    if unix_ts_ms > _ultimo_timestamp_ms:
        _ultimo_timestamp_ms = unix_ts_ms
        _ultimo_contador_aleatorio = (secrets.randbits(12) << 62) | secrets.randbits(62)
    else:
        unix_ts_ms = _ultimo_timestamp_ms
        _ultimo_contador_aleatorio += 1
        if _ultimo_contador_aleatorio >= (1 << 74):
            _ultimo_timestamp_ms += 1
            unix_ts_ms = _ultimo_timestamp_ms
            _ultimo_contador_aleatorio = (
                secrets.randbits(12) << 62
            ) | secrets.randbits(62)

    rand_a = (_ultimo_contador_aleatorio >> 62) & 0xFFF
    rand_b = _ultimo_contador_aleatorio & ((1 << 62) - 1)
    valor = (
        (unix_ts_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0b10 << 62)
        | rand_b
    )
    return uuid.UUID(int=valor)


class AuditLogImmutableError(AppException):
    """Error lanzado al intentar modificar o eliminar una entrada de auditoría."""

    status_code = 409
    code = "audit_log_inmutable"
    message = "El audit trail es inmutable y no admite modificaciones"


class PacienteInmutableError(AppException):
    """Error lanzado al alterar o eliminar un paciente ya evaluado."""

    status_code = 409
    code = "paciente_inmutable"
    message = "El paciente ya evaluado no admite alteraciones clínicas"


class Usuario(Base):
    """USUARIO: credenciales y rol con el que se firman las evaluaciones."""

    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint(
            "rol IN ('investigador', 'gestor')",
            name="ck_usuario_rol",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    rol: Mapped[str] = mapped_column(String(32), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    evaluaciones: Mapped[List["Evaluacion"]] = relationship(
        back_populates="usuario",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )
    auditorias: Mapped[List["AuditLog"]] = relationship(
        back_populates="usuario", lazy="select", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.email} rol={self.rol} activo={self.activo}>"


class Paciente(Base):
    """PACIENTE: sujeto evaluado, con los campos de PII ya enmascarados."""

    __tablename__ = "paciente"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    codigo_interno: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    seudonimo: Mapped[str] = mapped_column(String(128), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    genero: Mapped[str] = mapped_column(String(32), nullable=False)
    datos_clinicos: Mapped[str] = mapped_column(Text, nullable=False, default="")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    evaluaciones: Mapped[List["Evaluacion"]] = relationship(
        back_populates="paciente",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )
    medicaciones: Mapped[List["Medicacion"]] = relationship(
        back_populates="paciente",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )
    condiciones_medicas: Mapped[List["CondicionMedica"]] = relationship(
        back_populates="paciente",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Paciente {self.codigo_interno} activo={self.activo}>"


class Protocolo(Base):
    """PROTOCOLO: versión vigente del estudio con sus criterios de evaluación."""

    __tablename__ = "protocolo"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    fecha_vigencia: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")

    criterios: Mapped[List["Criterio"]] = relationship(
        back_populates="protocolo",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )
    evaluaciones: Mapped[List["Evaluacion"]] = relationship(
        back_populates="protocolo",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Protocolo {self.nombre} v{self.version}>"


class Criterio(Base):
    """CRITERIO: condición de inclusión o exclusión de un protocolo."""

    __tablename__ = "criterio"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('inclusion', 'exclusion')",
            name="ck_criterio_tipo",
        ),
        UniqueConstraint(
            "protocolo_id", "codigo", name="uq_criterio_protocolo_codigo"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    protocolo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("protocolo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(String(16), nullable=False)
    codigo: Mapped[str] = mapped_column(String(64), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    umbral: Mapped[str] = mapped_column(Text, nullable=False, default="")

    protocolo: Mapped["Protocolo"] = relationship(
        back_populates="criterios", lazy="joined", passive_updates=True
    )
    reglas_evaluacion: Mapped[List["ReglaEvaluacion"]] = relationship(
        back_populates="criterio",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Criterio {self.codigo} tipo={self.tipo}>"


class Medicacion(Base):
    """MEDICACION: tratamiento declarado por el paciente."""

    __tablename__ = "medicacion"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paciente.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tipo: Mapped[str] = mapped_column(String(64), nullable=False)

    paciente: Mapped["Paciente"] = relationship(
        back_populates="medicaciones", lazy="joined", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<Medicacion {self.nombre} tipo={self.tipo}>"


class CondicionMedica(Base):
    """CONDICION_MEDICA: antecedente clínico relevante del paciente."""

    __tablename__ = "condicion_medica"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paciente.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    diagnostico: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha_diagnostico: Mapped[date] = mapped_column(Date, nullable=False)
    detalle: Mapped[str] = mapped_column(Text, nullable=False, default="")

    paciente: Mapped["Paciente"] = relationship(
        back_populates="condiciones_medicas", lazy="joined", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<CondicionMedica {self.diagnostico}>"


class Evaluacion(Base):
    """EVALUACION: veredicto de pre-selección firmado por un investigador."""

    __tablename__ = "evaluacion"
    __table_args__ = (
        CheckConstraint(
            "resultado IS NULL OR resultado IN ('elegible', 'noElegible', 'pendiente')",
            name="ck_evaluacion_resultado",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'completada', 'en_revision')",
            name="ck_evaluacion_estado",
        ),
        Index("ix_evaluacion_paciente_fecha", "paciente_id", "fecha_evaluacion"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paciente.id"),
        nullable=False,
        index=True,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id"),
        nullable=False,
        index=True,
    )
    protocolo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("protocolo.id"),
        nullable=False,
        index=True,
    )
    fecha_evaluacion: Mapped[date] = mapped_column(Date, nullable=False)
    resultado: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    estado: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pendiente"
    )

    paciente: Mapped["Paciente"] = relationship(
        back_populates="evaluaciones", lazy="joined", passive_updates=True
    )
    usuario: Mapped["Usuario"] = relationship(
        back_populates="evaluaciones", lazy="joined", passive_updates=True
    )
    protocolo: Mapped["Protocolo"] = relationship(
        back_populates="evaluaciones", lazy="joined", passive_updates=True
    )
    reglas: Mapped[List["ReglaEvaluacion"]] = relationship(
        back_populates="evaluacion",
        lazy="select",
        passive_updates=True,
        passive_deletes=True,
    )
    auditorias: Mapped[List["AuditLog"]] = relationship(
        back_populates="evaluacion", lazy="select", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<Evaluacion {self.id} resultado={self.resultado} estado={self.estado}>"


class ReglaEvaluacion(Base):
    """REGLA_EVALUACION: detalle de cómo se evaluó cada criterio del protocolo."""

    __tablename__ = "regla_evaluacion"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("evaluacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterio_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("criterio.id"),
        nullable=False,
        index=True,
    )
    cumple: Mapped[bool] = mapped_column(Boolean, nullable=False)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    valor_paciente: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbral_evaluado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evaluacion: Mapped["Evaluacion"] = relationship(
        back_populates="reglas", lazy="joined", passive_updates=True
    )
    criterio: Mapped["Criterio"] = relationship(
        back_populates="reglas_evaluacion", lazy="joined", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<ReglaEvaluacion criterio={self.criterio_id} cumple={self.cumple}>"


class AuditLog(Base):
    """AUDIT_LOG: registro inmutable de trazabilidad con hash encadenado."""

    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_evaluacion", "evaluacion_id"),
        Index("ix_audit_log_usuario", "usuario_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=generate_uuid7
    )
    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("evaluacion.id"),
        nullable=False,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id"),
        nullable=False,
    )
    fecha_registro: Mapped[date] = mapped_column(Date, nullable=False)
    regla_rechazo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    detalle: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hash_encadenado: Mapped[str] = mapped_column(String(128), nullable=False)

    evaluacion: Mapped["Evaluacion"] = relationship(
        back_populates="auditorias", lazy="joined", passive_updates=True
    )
    usuario: Mapped["Usuario"] = relationship(
        back_populates="auditorias", lazy="joined", passive_updates=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.id} evaluacion={self.evaluacion_id}>"


@event.listens_for(AuditLog, "before_update")
def bloquear_actualizacion_audit_log(mapper, connection, target) -> None:
    """Impide actualizar una entrada ya registrada en el audit trail.

    Raises:
        AuditLogImmutableError: Siempre; el audit trail es inmutable.
    """
    raise AuditLogImmutableError(
        "El audit trail es inmutable: no se pueden modificar sus registros"
    )


@event.listens_for(AuditLog, "before_delete")
def bloquear_borrado_audit_log(mapper, connection, target) -> None:
    """Impide eliminar una entrada del audit trail.

    Raises:
        AuditLogImmutableError: Siempre; el audit trail es inmutable.
    """
    raise AuditLogImmutableError(
        "El audit trail es inmutable: no se pueden eliminar sus registros"
    )


@event.listens_for(Paciente, "before_update")
def bloquear_alteraciones_de_pacientes_evaluados(mapper, connection, target) -> None:
    """Impide alterar los datos clínicos de un paciente ya evaluado.

    El cambio del indicador ``activo`` (borrado lógico) sí está permitido en
    cualquier momento, tal y como exige el requisito de protección de
    registros pasados.

    Raises:
        PacienteInmutableError: Si el paciente ya tiene evaluaciones y se
            modifican campos distintos de ``activo``.
    """
    estado = inspect(target)
    campos_alterados = [
        nombre
        for nombre in estado.mapper.columns.keys()
        if nombre != "activo" and estado.attrs[nombre].history.has_changes()
    ]
    if not campos_alterados:
        return

    evaluacion_existente = connection.execute(
        select(Evaluacion.id).where(Evaluacion.paciente_id == target.id).limit(1)
    ).first()
    if evaluacion_existente is not None:
        raise PacienteInmutableError(
            "El paciente ya ha sido evaluado: sus datos clínicos no pueden modificarse"
        )


@event.listens_for(Paciente, "before_delete")
def bloquear_borrado_paciente(mapper, connection, target) -> None:
    """Impide el borrado físico de pacientes.

    El registro se conserva y se marca como inactivo mediante ``activo``,
    respetando la trazabilidad clínica y la normativa de protección de datos.

    Raises:
        PacienteInmutableError: Siempre; el borrado físico está deshabilitado.
    """
    raise PacienteInmutableError(
        "El borrado de pacientes está deshabilitado: utilice el borrado lógico "
        "marcando el registro como inactivo"
    )


__all__ = [
    "AuditLog",
    "AuditLogImmutableError",
    "CondicionMedica",
    "Criterio",
    "ESTADOS_EVALUACION_VALIDOS",
    "Evaluacion",
    "Medicacion",
    "Paciente",
    "PacienteInmutableError",
    "Protocolo",
    "RESULTADOS_EVALUACION_VALIDOS",
    "ROLES_VALIDOS",
    "ReglaEvaluacion",
    "TIPOS_CRITERIO_VALIDOS",
    "Usuario",
    "generate_uuid7",
]
