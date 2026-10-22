"""Utilidades transversales de privacidad clínica y trazabilidad GxP.

El módulo concentra las dos primitivas que el resto de la aplicación necesita
para cumplir la normativa de privacidad clínica (GDPR/HIPAA) y los requisitos
de audit trail del ensayo ALM-PSO-2026:

* :func:`mask_pii_data`: enmascara los campos de identificación personal (PII)
  antes de exponerlos en la interfaz, en las respuestas de la API o en los
  registros de trazabilidad. Los valores enmascarados conservan únicamente
  los primeros y los últimos caracteres, de modo que el registro siga siendo
  identificable sin llegar a contener PII en claro.
* :func:`generate_chained_hash`: calcula el hash encadenado de cada entrada
  del audit trail. Cada hash depende del hash de la entrada anterior, por lo
  que cualquier modificación de un registro pasado invalida la cadena y resulta
  detectable (requisito de inmutabilidad GxP).

Las utilidades sólo dependen de la biblioteca estándar, de modo que puedan
importarse desde cualquier capa (servicios, motor de reglas, API) sin crear
acoplamiento con la persistencia ni con la configuración del entorno.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

PII_FIELDS: Tuple[str, ...] = (
    "codigo_interno",
    "seudonimo",
    "datos_clinicos",
)
"""Campos de `PACIENTE` tratados como PII y enmascarados por defecto."""

MASK_CHARACTER = "*"
"""Carácter utilizado para ocultar los caracteres enmascarados."""

GENESIS_HASH = "0" * 64
"""Hash inicial de la cadena de auditoría (primera entrada del audit trail)."""


def mask_value(
    value: Optional[str],
    visible_start: int = 2,
    visible_end: int = 2,
    mask_character: str = MASK_CHARACTER,
) -> str:
    """Enmascara una cadena conservando únicamente los caracteres indicados.

    Args:
        value: Valor de origen. Si es `None` se devuelve una cadena vacía.
        visible_start: Número de caracteres iniciales que se mantienen visibles.
        visible_end: Número de caracteres finales que se mantienen visibles.
        mask_character: Carácter con el que se sustituye el resto.

    Returns:
        Cadena enmascarada. Para valores demasiado cortos se conserva como
        máximo `visible_start` caracteres y el resto queda enmascarado.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    if not value:
        return ""
    if visible_start < 0 or visible_end < 0:
        raise ValueError("El número de caracteres visibles no puede ser negativo")
    if not mask_character:
        raise ValueError("El carácter de enmascaramiento no puede estar vacío")

    total_visible = visible_start + visible_end
    if len(value) <= total_visible:
        keep = min(visible_start, len(value) - 1)
        return value[:keep] + mask_character * (len(value) - keep)

    inicio = value[:visible_start]
    fin = value[-visible_end:] if visible_end else ""
    return inicio + mask_character * (len(value) - total_visible) + fin


def mask_pii_data(
    data: Optional[Mapping[str, Any]],
    fields: Optional[Iterable[str]] = None,
    visible_start: int = 2,
    visible_end: int = 2,
    mask_character: str = MASK_CHARACTER,
) -> Dict[str, Any]:
    """Devuelve una copia del diccionario con los campos de PII enmascarados.

    El diccionario original no se modifica. Los valores anidados que sean
    diccionarios o listas de diccionarios se recorren de forma recursiva,
    de modo que ningún PII queda sin enmascarar dentro de la estructura.

    Args:
        data: Diccionario de datos de partida. Si es `None` se devuelve un
            diccionario vacío.
        fields: Campos a enmascarar. Por defecto se usan `PII_FIELDS`.
        visible_start: Caracteres iniciales visibles de cada valor.
        visible_end: Caracteres finales visibles de cada valor.
        mask_character: Carácter con el que se sustituye el resto.

    Returns:
        Copia del diccionario con los campos de PII enmascarados.

    Raises:
        TypeError: Si `data` no es un diccionario ni es `None`.
    """
    campos = tuple(fields) if fields is not None else PII_FIELDS
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise TypeError("mask_pii_data espera un diccionario de datos")

    resultado: Dict[str, Any] = {}
    for clave, valor in data.items():
        if clave in campos:
            resultado[clave] = _mask_generic_value(
                valor,
                campos,
                visible_start=visible_start,
                visible_end=visible_end,
                mask_character=mask_character,
            )
        elif isinstance(valor, Mapping):
            resultado[clave] = mask_pii_data(
                valor,
                campos,
                visible_start=visible_start,
                visible_end=visible_end,
                mask_character=mask_character,
            )
        elif isinstance(valor, (list, tuple)):
            resultado[clave] = [
                mask_pii_data(
                    item,
                    campos,
                    visible_start=visible_start,
                    visible_end=visible_end,
                    mask_character=mask_character,
                )
                if isinstance(item, Mapping)
                else item
                for item in valor
            ]
        else:
            resultado[clave] = valor
    return resultado


def generate_chained_hash(
    previous_hash: Optional[Any] = None,
    payload: Optional[Mapping[str, Any]] = None,
    **fields: Any,
) -> str:
    """Calcula el hash encadenado de una entrada del audit trail.

    El hash resultante es SHA-256 sobre el hash de la entrada anterior
    concatenado con la representación canónica (JSON ordenado) de los datos de
    la entrada. De este modo, alterar una entrada previa invalida todos los
    hashes posteriores y la manipulación del registro es detectable.

    Args:
        previous_hash: Hash de la entrada anterior. Si es `None` se usa
            `GENESIS_HASH`. También admite un diccionario como primer
            argumento, interpretándolo como el payload de la entrada.
        payload: Datos de la entrada (por ejemplo, identificadores, fecha y
            detalle de la regla aplicada).
        **fields: Campos adicionales del payload, expresados como argumentos
            con nombre.

    Returns:
        Hash hexadecimal de 64 caracteres.

    Raises:
        TypeError: Si el payload no es un diccionario.
    """
    anterior = GENESIS_HASH
    datos: Dict[str, Any] = {}

    if isinstance(previous_hash, Mapping):
        if payload is None:
            datos.update(previous_hash)
        else:
            raise TypeError(
                "No se puede combinar un payload posicional con un hash previo"
            )
        anterior = GENESIS_HASH
    elif previous_hash is not None:
        anterior = str(previous_hash).strip() or GENESIS_HASH

    if payload is not None:
        if not isinstance(payload, Mapping):
            raise TypeError("El payload del hash encadenado debe ser un diccionario")
        datos.update(payload)

    datos.update(fields)

    documento = json.dumps(
        datos,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(f"{anterior}|{documento}".encode("utf-8")).hexdigest()


def verify_chained_hash(
    entry: Mapping[str, Any],
    previous_hash: Optional[str] = None,
) -> bool:
    """Comprueba que el hash almacenado en una entrada del audit trail es válido.

    Args:
        entry: Entrada de auditoría. El campo `hash_encadenado` se excluye del
            payload recalculado.
        previous_hash: Hash de la entrada anterior. Si es `None` se usa
            `GENESIS_HASH`.

    Returns:
        `True` cuando el hash recalculado coincide con el almacenado.

    Raises:
        TypeError: Si `entry` no es un diccionario.
    """
    if not isinstance(entry, Mapping):
        raise TypeError("verify_chained_hash espera un diccionario de la entrada")
    payload = {clave: valor for clave, valor in entry.items() if clave != "hash_encadenado"}
    esperado = generate_chained_hash(previous_hash, payload)
    return hmac.compare_digest(esperado, str(entry.get("hash_encadenado", "")))


def _mask_generic_value(
    value: Any,
    campos: Tuple[str, ...],
    visible_start: int,
    visible_end: int,
    mask_character: str,
) -> Any:
    """Enmascara un valor conservando la estructura original del dato."""
    if value is None:
        return None
    if isinstance(value, str):
        return mask_value(
            value,
            visible_start=visible_start,
            visible_end=visible_end,
            mask_character=mask_character,
        )
    if isinstance(value, Mapping):
        return mask_pii_data(
            value,
            campos,
            visible_start=visible_start,
            visible_end=visible_end,
            mask_character=mask_character,
        )
    if isinstance(value, (list, tuple)):
        elementos: List[Any] = [
            _mask_generic_value(
                item,
                campos,
                visible_start=visible_start,
                visible_end=visible_end,
                mask_character=mask_character,
            )
            for item in value
        ]
        return elementos
    return value


__all__ = [
    "GENESIS_HASH",
    "MASK_CHARACTER",
    "PII_FIELDS",
    "generate_chained_hash",
    "mask_pii_data",
    "mask_value",
    "verify_chained_hash",
]
