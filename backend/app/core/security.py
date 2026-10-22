"""Primitivas de seguridad: tokens JWT y hashing de contraseñas.

El módulo concentra la emisión y verificación de tokens de acceso (python-jose)
y el hashing y verificación de contraseñas (passlib), de modo que el resto de
la aplicación no dependa de la biblioteca criptográfica concreta.

La resolución del usuario autenticado se apoya en la sesión de base de datos,
cuya dependencia se resuelve de forma diferida para no acoplar este módulo a
la capa de persistencia en tiempo de importación.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.core.config import settings
from backend.app.core.exceptions import ConfigurationException, UnauthorizedException

PASSWORD_SCHEME = "pbkdf2_sha256"
"""Esquema de hashing de contraseñas utilizado para almacenar credenciales."""

PASSWORD_SCHEMES = (PASSWORD_SCHEME,)
"""Esquemas aceptados al verificar contraseñas ya almacenadas."""

pwd_context = CryptContext(schemes=list(PASSWORD_SCHEMES), deprecated="auto")

oauth2_scheme = HTTPBearer(auto_error=False)
"""Esquema de seguridad Bearer (JWT) utilizado en la cabecera Authorization."""


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña en texto plano.

    Args:
        password: Contraseña en texto plano.

    Returns:
        Hash con el esquema configurado, listo para persistir.
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash almacenado.

    Args:
        plain_password: Contraseña introducida por el usuario.
        hashed_password: Hash persistido de la contraseña.

    Returns:
        `True` cuando la contraseña coincide, `False` en caso contrario.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT de acceso.

    Args:
        data: Claims del token; se espera `sub` con el correo del usuario.
        expires_delta: Vigencia concreta; por defecto se usa
            `ACCESS_TOKEN_EXPIRE_MINUTES`.

    Returns:
        Token JWT firmado y codificado.
    """
    secret_key = _require_secret_key()
    to_encode: Dict[str, Any] = dict(data)
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expires_at,
            "iat": issued_at,
            "jti": uuid4().hex,
            "typ": "access",
        }
    )
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida un token JWT de acceso.

    Args:
        token: Token presentado en la cabecera Authorization.

    Returns:
        Claims del token.

    Raises:
        UnauthorizedException: Si el token es inválido, ha expirado o no
            identifica a ningún usuario.
    """
    secret_key = _require_secret_key()
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedException("El token de acceso es inválido o ha expirado") from exc
    if not payload.get("sub"):
        raise UnauthorizedException("El token de acceso no identifica a ningún usuario")
    return payload


def get_db_session():
    """Entrega la sesión de base de datos a la aplicación.

    El módulo de persistencia se importa de forma diferida para mantener
    este módulo independiente de la capa de datos.

    Yields:
        Sesión de SQLAlchemy activa durante la petición.
    """
    from backend.database.session import get_db

    session_dependency = get_db()
    if inspect.isgenerator(session_dependency):
        yield from session_dependency
    else:
        yield session_dependency


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
    db: Any = Depends(get_db_session),
) -> Any:
    """Resuelve el usuario autenticado de la petición a partir del token JWT.

    Args:
        credentials: Credenciales Bearer extraídas de la cabecera Authorization.
        db: Sesión de base de datos de la petición.

    Returns:
        El usuario autenticado.

    Raises:
        UnauthorizedException: Si faltan las credenciales, el token no es
            válido o el usuario no existe o está inactivo.
    """
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Faltan las credenciales de autenticación")

    payload = decode_access_token(credentials.credentials)
    email = payload.get("sub")
    usuario = _find_usuario_by_email(db, email)
    if usuario is None:
        raise UnauthorizedException("El usuario del token no está registrado")
    if not getattr(usuario, "activo", True):
        raise UnauthorizedException("El usuario está inactivo")
    return usuario


def _find_usuario_by_email(db: Any, email: str) -> Any:
    """Busca un usuario por correo en la base de datos."""
    from sqlalchemy import select

    from backend.database.models import Usuario

    result = db.execute(select(Usuario).where(Usuario.email == email))
    return result.scalars().first()


def _require_secret_key() -> str:
    """Devuelve la clave de firma o aborta si el entorno no la proporciona."""
    if not settings.SECRET_KEY:
        raise ConfigurationException(
            "La variable de entorno SECRET_KEY no está configurada"
        )
    return settings.SECRET_KEY


__all__ = [
    "PASSWORD_SCHEMES",
    "PASSWORD_SCHEME",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_db_session",
    "get_password_hash",
    "oauth2_scheme",
    "pwd_context",
    "verify_password",
]
