"""Operaciones CRUD genéricas sobre los modelos ORM.

La clase :class:`CRUDBase` encapsula las operaciones habituales (alta,
lectura, listado con filtros, actualización y borrado) para que la capa de
servicios no tenga que construir sentencias SQL a mano. Cada instancia está
ligada a un modelo concreto y se parametrizan con una sesión de SQLAlchemy.

Las instancias de uso frecuente se exportan ya inicializadas
(``usuario_crud``, ``paciente_crud``…) para evitar su construcción repetida en
los routers.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

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

ModelType = TypeVar("ModelType")


def _confirmar(db: Session) -> None:
    """Confirma la transacción revirtiéndola si la confirmación falla.

    Las reglas de integridad del dominio (inmutabilidad del audit trail,
    pacientes ya evaluados) se aplican durante el vaciado de la sesión. Si
    alguna de ellas se incumple, la transacción se revierte para dejar la
    sesión en un estado utilizable y el error se propaga al llamante.

    Args:
        db: Sesión de base de datos.

    Raises:
        Exception: La excepción original producida por la confirmación.
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


class CRUDBase(Generic[ModelType]):
    """Operaciones CRUD genéricas sobre un modelo ORM.

    Attributes:
        model: Clase ORM sobre la que se construyen las sentencias.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def create(self, db: Session, obj: ModelType, *, commit: bool = True) -> ModelType:
        """Persiste un objeto nuevo.

        Args:
            db: Sesión de base de datos.
            obj: Instancia del modelo a persistir.
            commit: Si es ``True``, confirma la transacción.

        Returns:
            El objeto persistido, ya refrescado.
        """
        db.add(obj)
        if commit:
            _confirmar(db)
            db.refresh(obj)
        else:
            db.flush()
        return obj

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Obtiene un registro por su identificador.

        Args:
            db: Sesión de base de datos.
            id: Identificador primary key.

        Returns:
            El registro o ``None`` si no existe.
        """
        return db.get(self.model, id)

    def get_by(self, db: Session, **filters: Any) -> Optional[ModelType]:
        """Obtiene el primer registro que cumple los filtros indicados.

        Args:
            db: Sesión de base de datos.
            **filters: Igualdad por atributo; los valores ``None`` se ignoran.

        Returns:
            El primer registro encontrado o ``None``.
        """
        stmt = self._aplicar_filtros(select(self.model), filters)
        return db.execute(stmt).scalars().first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
    ) -> List[ModelType]:
        """Lista registros aplicando filtros, orden y paginación.

        Args:
            db: Sesión de base de datos.
            skip: Número de registros a omitir.
            limit: Máximo de registros a devolver.
            filters: Filtros de igualdad por atributo.
            order_by: Expresión de ordenación opcional.

        Returns:
            Lista de registros.
        """
        stmt = self._aplicar_filtros(select(self.model), filters or {})
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def update(
        self,
        db: Session,
        obj: ModelType,
        *,
        commit: bool = True,
        **values: Any,
    ) -> ModelType:
        """Actualiza los atributos indicados de un registro.

        Args:
            db: Sesión de base de datos.
            obj: Registro a actualizar.
            commit: Si es ``True``, confirma la transacción.
            **values: Nuevos valores por nombre de atributo.

        Returns:
            El registro actualizado.

        Raises:
            AttributeError: Si algún atributo no existe en el modelo.
        """
        for campo, valor in values.items():
            if not hasattr(obj, campo):
                raise AttributeError(
                    f"El modelo {self.model.__name__} no define el campo '{campo}'"
                )
            setattr(obj, campo, valor)
        if commit:
            _confirmar(db)
            db.refresh(obj)
        else:
            db.flush()
        return obj

    def remove(self, db: Session, id: Any, *, commit: bool = True) -> bool:
        """Elimina un registro por su identificador.

        Args:
            db: Sesión de base de datos.
            id: Identificador primary key.
            commit: Si es ``True``, confirma la transacción.

        Returns:
            ``True`` si el registro existía y se ha eliminado.
        """
        obj = self.get(db, id)
        if obj is None:
            return False
        db.delete(obj)
        if commit:
            _confirmar(db)
        else:
            db.flush()
        return True

    def exists(self, db: Session, **filters: Any) -> bool:
        """Comprueba si existe al menos un registro con los filtros indicados.

        Args:
            db: Sesión de base de datos.
            **filters: Igualdad por atributo; los valores ``None`` se ignoran.

        Returns:
            ``True`` si hay al menos una coincidencia.
        """
        stmt = self._aplicar_filtros(select(1).select_from(self.model), filters)
        return db.execute(stmt.limit(1)).first() is not None

    def count(self, db: Session, **filters: Any) -> int:
        """Cuenta los registros que cumplen los filtros indicados.

        Args:
            db: Sesión de base de datos.
            **filters: Igualdad por atributo; los valores ``None`` se ignoran.

        Returns:
            Número de registros coincidentes.
        """
        stmt = self._aplicar_filtros(
            select(func.count()).select_from(self.model), filters
        )
        return int(db.execute(stmt).scalar() or 0)

    def _aplicar_filtros(
        self, stmt: Select, filters: Dict[str, Any]
    ) -> Select:
        """Aplica filtros de igualdad (o pertenencia) sobre una sentencia.

        Args:
            stmt: Sentencia base.
            filters: Filtros por nombre de atributo.

        Returns:
            Sentencia con los filtros aplicados.

        Raises:
            AttributeError: Si algún filtro no corresponde a un atributo del
                modelo.
        """
        for campo, valor in filters.items():
            if valor is None:
                continue
            atributo = getattr(self.model, campo, None)
            if atributo is None:
                raise AttributeError(
                    f"El modelo {self.model.__name__} no define el campo '{campo}'"
                )
            if isinstance(valor, (list, tuple, set, frozenset)):
                stmt = stmt.where(atributo.in_(list(valor)))
            else:
                stmt = stmt.where(atributo == valor)
        return stmt


usuario_crud = CRUDBase(Usuario)
paciente_crud = CRUDBase(Paciente)
protocolo_crud = CRUDBase(Protocolo)
criterio_crud = CRUDBase(Criterio)
medicacion_crud = CRUDBase(Medicacion)
condicion_medica_crud = CRUDBase(CondicionMedica)
evaluacion_crud = CRUDBase(Evaluacion)
regla_evaluacion_crud = CRUDBase(ReglaEvaluacion)
audit_log_crud = CRUDBase(AuditLog)


__all__ = [
    "CRUDBase",
    "ModelType",
    "audit_log_crud",
    "criterio_crud",
    "condicion_medica_crud",
    "evaluacion_crud",
    "medicacion_crud",
    "paciente_crud",
    "protocolo_crud",
    "regla_evaluacion_crud",
    "usuario_crud",
]
