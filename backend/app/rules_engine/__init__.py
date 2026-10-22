"""Primitivas compartidas del motor de reglas de pre-selección clínica.

El motor evalúa, mediante reglas booleanas, los criterios de inclusión y de
exclusión de un protocolo clínico y devuelve un veredicto trazable: cada
criterio evaluado queda registrado con el valor observado en el paciente, el
umbral aplicado y, cuando procede, el motivo del rechazo.

Este módulo define los tipos genéricos que reutiliza cualquier implementación
de protocolo (por ejemplo, ``protocol_alm_pso_2026``):

* :class:`TipoCriterio`: naturaleza del criterio (inclusión o exclusión).
* :class:`ResultadoProtocolo`: veredicto global emitido por el motor.
* :class:`ReglaEvaluada`: resultado de evaluar un criterio concreto.
* :class:`ResultadoEvaluacionProtocolo`: veredicto agregado con las reglas.
* :func:`construir_resultado_protocolo`: agrega las reglas en un veredicto.

Las primitivas son deliberadamente independientes del protocolo concreto y de
la capa de persistencia para mantener el motor sin dependencias de entrada y
con latencia mínima.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional


class TipoCriterio(str, Enum):
    """Naturaleza de un criterio dentro de un protocolo clínico."""

    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"


class ResultadoProtocolo(str, Enum):
    """Veredicto global emitido por el motor de reglas."""

    ELEGIBLE = "elegible"
    NO_ELEGIBLE = "noElegible"


@dataclass(frozen=True)
class ReglaEvaluada:
    """Resultado de evaluar un criterio del protocolo contra un paciente.

    Attributes:
        criterio_codigo: Código del criterio evaluado (por ejemplo ``EDAD_MIN_18``).
        tipo: Si el criterio es de inclusión o de exclusión.
        cumple: ``True`` cuando el paciente satisface el criterio.
        valor_paciente: Valor observado en el paciente, ya formateado.
        umbral_evaluado: Umbral del criterio aplicado en la comparación.
        motivo_rechazo: Motivo legible del incumplimiento, si lo hay.
    """

    criterio_codigo: str
    tipo: TipoCriterio
    cumple: bool
    valor_paciente: Optional[str] = None
    umbral_evaluado: Optional[str] = None
    motivo_rechazo: Optional[str] = None

    @property
    def es_inclusion(self) -> bool:
        """Indica si el criterio es de inclusión."""
        return self.tipo == TipoCriterio.INCLUSION

    @property
    def es_exclusion(self) -> bool:
        """Indica si el criterio es de exclusión."""
        return self.tipo == TipoCriterio.EXCLUSION


@dataclass(frozen=True)
class ResultadoEvaluacionProtocolo:
    """Veredicto agregado de la evaluación de un protocolo.

    Attributes:
        resultado: Veredicto global (`elegible` / `noElegible`).
        elegible: ``True`` cuando el paciente cumple todos los criterios.
        reglas: Detalle de cada criterio evaluado.
    """

    resultado: ResultadoProtocolo
    elegible: bool
    reglas: List[ReglaEvaluada] = field(default_factory=list)

    @property
    def criterios_incumplidos(self) -> List[ReglaEvaluada]:
        """Criterios que el paciente no ha superado."""
        return [regla for regla in self.reglas if not regla.cumple]

    @property
    def motivos_rechazo(self) -> List[str]:
        """Motivos de rechazo, en orden de evaluación, sin duplicados."""
        motivos: List[str] = []
        for regla in self.criterios_incumplidos:
            motivo = regla.motivo_rechazo or (
                f"Criterio incumplido: {regla.criterio_codigo}"
            )
            if motivo not in motivos:
                motivos.append(motivo)
        return motivos

    def reglas_por_tipo(self, tipo: TipoCriterio) -> List[ReglaEvaluada]:
        """Devuelve las reglas evaluadas del tipo indicado."""
        return [regla for regla in self.reglas if regla.tipo == tipo]


def construir_resultado_protocolo(
    reglas: Iterable[ReglaEvaluada],
) -> ResultadoEvaluacionProtocolo:
    """Agrega el detalle por criterio en el veredicto global del protocolo.

    Un paciente es elegible cuando todos los criterios evaluados se cumplen:
    los criterios de inclusión deben cumplirse y los de exclusión no deben
    incumplirse.

    Args:
        reglas: Detalle de cada criterio evaluado contra el paciente.

    Returns:
        Veredicto agregado con el resultado y el detalle de las reglas.
    """
    evaluadas: List[ReglaEvaluada] = list(reglas)
    elegible = all(regla.cumple for regla in evaluadas)
    resultado = (
        ResultadoProtocolo.ELEGIBLE if elegible else ResultadoProtocolo.NO_ELEGIBLE
    )
    return ResultadoEvaluacionProtocolo(
        resultado=resultado,
        elegible=elegible,
        reglas=evaluadas,
    )


def evaluar_criterio(
    criterio_codigo: str,
    tipo: TipoCriterio,
    cumple: bool,
    valor_paciente: Optional[str] = None,
    umbral_evaluado: Optional[str] = None,
    motivo_rechazo: Optional[str] = None,
) -> ReglaEvaluada:
    """Construye el detalle de un criterio evaluado.

    Args:
        criterio_codigo: Código del criterio evaluado.
        tipo: Naturaleza del criterio.
        cumple: Resultado de la comparación booleana.
        valor_paciente: Valor observado en el paciente.
        umbral_evaluado: Umbral aplicado en la comparación.
        motivo_rechazo: Motivo legible del incumplimiento.

    Returns:
        Instancia de :class:`ReglaEvaluada` lista para persistir.
    """
    return ReglaEvaluada(
        criterio_codigo=criterio_codigo,
        tipo=tipo,
        cumple=cumple,
        valor_paciente=valor_paciente,
        umbral_evaluado=umbral_evaluado,
        motivo_rechazo=motivo_rechazo if not cumple else None,
    )


def formatear_valor(valor: object, unidad: str = "") -> str:
    """Formatea un valor clínico para trazarlo en la regla evaluada.

    Args:
        valor: Valor a formatear.
        unidad: Unidad opcional (por ejemplo ``%``).

    Returns:
        Representación textual estable del valor.
    """
    if valor is None:
        return "no registrado"
    if isinstance(valor, bool):
        texto = "sí" if valor else "no"
    elif isinstance(valor, float):
        texto = f"{valor:g}"
    else:
        texto = str(valor)
    if unidad:
        return f"{texto} {unidad}"
    return texto


__all__ = [
    "ReglaEvaluada",
    "ResultadoEvaluacionProtocolo",
    "ResultadoProtocolo",
    "TipoCriterio",
    "construir_resultado_protocolo",
    "evaluar_criterio",
    "formatear_valor",
]
