"""Excepciones del dominio y manejadores de respuestas de error estructuradas.

Las excepciones de negocio heredan de `AppException` y llevan consigo el
código HTTP y un código estable. La API responde siempre con la misma
estructura:

```json
{"detail": "mensaje legible", "code": "not_found"}
```

Cuando hay detalles adicionales (por ejemplo, errores de validación de
esquema) se añaden en la clave `details`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

HTTP_422_UNPROCESSABLE = 422
"""Código HTTP de entidad no procesable (evita depender del alias deprecado de Starlette)."""

_STATUS_CODES: Dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
    status.HTTP_409_CONFLICT: "conflict",
    HTTP_422_UNPROCESSABLE: "validation_error",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
}


class AppException(Exception):
    """Excepción base de la aplicación."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    message: str = "Se produjo un error interno"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details: Dict[str, Any] = details or {}
        super().__init__(self.message)

    def to_payload(self) -> Dict[str, Any]:
        """Construye el cuerpo de la respuesta de error."""
        payload: Dict[str, Any] = {"detail": self.message, "code": self.code}
        if self.details:
            payload["details"] = self.details
        return payload


class ConfigurationException(AppException):
    """Error de configuración del entorno; impide el arranque del servicio."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "configuration_error"
    message = "La configuración de la aplicación no es válida"


class UnauthorizedException(AppException):
    """Falta la autenticación o el token presentado no es válido."""

    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "No se ha autenticado la petición"


class ForbiddenException(AppException):
    """El usuario autenticado no tiene permisos para la operación solicitada."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    message = "No tiene permisos para realizar esta operación"


class NotFoundException(AppException):
    """El recurso solicitado no existe."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "El recurso solicitado no existe"


class ConflictException(AppException):
    """El recurso ya existe o entra en conflicto con el estado actual."""

    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "El recurso entra en conflicto con el estado actual"


class BusinessRuleException(AppException):
    """La operación infringe una regla de negocio (por ejemplo, clínica)."""

    status_code = HTTP_422_UNPROCESSABLE
    code = "business_rule_violation"
    message = "La operación infringe una regla de negocio"


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Convierte una `AppException` en una respuesta JSON estructurada."""
    headers = None
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        headers = {"WWW-Authenticate": "Bearer"}
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(exc.to_payload()),
        headers=headers,
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Normaliza las respuestas de error HTTP de FastAPI y Starlette."""
    detail = exc.detail if isinstance(exc.detail, str) else "La solicitud no pudo ser procesada"
    payload: Dict[str, Any] = {
        "detail": detail,
        "code": _STATUS_CODES.get(exc.status_code, "http_error"),
    }
    headers = dict(getattr(exc, "headers", None) or {})
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        headers.setdefault("WWW-Authenticate", "Bearer")
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(payload),
        headers=headers or None,
    )


def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Responde con el detalle de los errores de validación de esquemas."""
    errors: List[Dict[str, Any]] = [
        {
            "loc": [str(part) for part in error.get("loc", [])],
            "msg": str(error.get("msg", "")),
            "type": str(error.get("type", "")),
        }
        for error in exc.errors()
    ]
    payload: Dict[str, Any] = {
        "detail": "Los datos enviados no cumplen el esquema requerido",
        "code": "validation_error",
        "details": {"errors": errors},
    }
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE,
        content=jsonable_encoder(payload),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepciones estructurados en la aplicación."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)


__all__ = [
    "AppException",
    "BusinessRuleException",
    "ConfigurationException",
    "ConflictException",
    "ForbiddenException",
    "NotFoundException",
    "UnauthorizedException",
    "app_exception_handler",
    "http_exception_handler",
    "register_exception_handlers",
    "request_validation_exception_handler",
]
