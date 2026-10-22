"""Dependencias de FastAPI compartidas por los routers de la API.

El módulo centraliza el acceso a la base de datos y el control de acceso
basado en roles:

* ``get_db``: sesión de base de datos por petición.
* ``get_current_user``: usuario autenticado a partir del token JWT.
* ``get_current_active_user``: usuario autenticado y activo.
* ``get_current_active_investigador`` / ``get_current_active_gestor``: usuario
  autenticado con el rol requerido.

Los roles válidos son ``investigador`` y ``gestor``; el acceso con un rol
insuficiente devuelve 403 y la ausencia de sesión válida devuelve 401.
"""

from __future__ import annotations

from fastapi import Depends

from backend.app.core.exceptions import ForbiddenException, UnauthorizedException
from backend.app.core.security import get_current_user
from backend.database.models import Usuario
from backend.database.session import get_db

__all__ = [
    "get_current_active_gestor",
    "get_current_active_investigador",
    "get_current_active_user",
    "get_current_user",
    "get_db",
]


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """Devuelve el usuario autenticado, exigiendo que esté activo.

    Args:
        current_user: Usuario resuelto a partir del token JWT.

    Returns:
        El usuario autenticado y activo.

    Raises:
        UnauthorizedException: Si el usuario está inactivo.
    """
    if not current_user.activo:
        raise UnauthorizedException(
            "El usuario está inactivo y no puede operar el sistema",
            code="usuario_inactivo",
        )
    return current_user


def get_current_active_investigador(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    """Exige que el usuario autenticado tenga el rol ``investigador``.

    Args:
        current_user: Usuario autenticado y activo.

    Returns:
        El usuario autenticado con rol de investigador.

    Raises:
        ForbiddenException: Si el usuario no tiene el rol requerido.
    """
    if current_user.rol != "investigador":
        raise ForbiddenException(
            "Esta operación requiere el rol 'investigador'",
            code="rol_insuficiente",
        )
    return current_user


def get_current_active_gestor(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    """Exige que el usuario autenticado tenga el rol ``gestor``.

    Args:
        current_user: Usuario autenticado y activo.

    Returns:
        El usuario autenticado con rol de gestor.

    Raises:
        ForbiddenException: Si el usuario no tiene el rol requerido.
    """
    if current_user.rol != "gestor":
        raise ForbiddenException(
            "Esta operación requiere el rol 'gestor'",
            code="rol_insuficiente",
        )
    return current_user
