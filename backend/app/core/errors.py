import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorRespuesta(BaseModel):
    code: str
    message: str


class ErrorApp(Exception):
    status_code: int = 500
    code: str = "error_interno"
    message: str = "Ocurrió un error interno."
    headers: dict[str, str] | None = None

    def __init__(self, message: str | None = None, headers: dict[str, str] | None = None) -> None:
        if message is not None:
            self.message = message
        if headers is not None:
            self.headers = headers
        super().__init__(self.message)


class NoEncontrado(ErrorApp):
    status_code = 404
    code = "no_encontrado"
    message = "No se encontró el recurso solicitado."


class NoAutenticado(ErrorApp):
    status_code = 401
    code = "no_autenticado"
    message = "Debes iniciar sesión para continuar."


class SinPermiso(ErrorApp):
    status_code = 403
    code = "sin_permiso"
    message = "No tienes permiso para realizar esta acción."


class Conflicto(ErrorApp):
    status_code = 409
    code = "conflicto"
    message = "La operación entra en conflicto con el estado actual."


class DocumentoDuplicado(Conflicto):
    code = "documento_duplicado"
    message = "Este documento ya fue subido"


class ArchivoNoValido(ErrorApp):
    status_code = 415
    code = "archivo_no_valido"
    message = "El archivo no es un PDF válido."


class ArchivoDemasiadoGrande(ErrorApp):
    status_code = 413
    code = "archivo_demasiado_grande"
    message = "El archivo supera el tamaño máximo permitido."


class ReglaDeNegocio(ErrorApp):
    status_code = 422
    code = "regla_de_negocio"
    message = "La operación no cumple una regla del sistema."


class SesionExpirada(NoAutenticado):
    code = "sesion_expirada"
    message = "Tu sesión se cerró por inactividad. Inicia sesión de nuevo."


class ServicioNoDisponible(ErrorApp):
    status_code = 503
    code = "servicio_no_disponible"
    message = "El servicio no está disponible. Intenta de nuevo en unos minutos."


class DemasiadosIntentos(ErrorApp):
    status_code = 429
    code = "demasiados_intentos"
    message = "Demasiados intentos. Intenta de nuevo más tarde."


MENSAJES_HTTP = {
    401: ("no_autenticado", "Debes iniciar sesión para continuar."),
    403: ("sin_permiso", "No tienes permiso para realizar esta acción."),
    404: ("no_encontrado", "No se encontró el recurso solicitado."),
    405: ("metodo_no_permitido", "Método no permitido para esta ruta."),
}


def _respuesta(
    status_code: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    cuerpo = ErrorRespuesta(code=code, message=message)
    return JSONResponse(status_code=status_code, content=cuerpo.model_dump(), headers=headers)


async def manejar_error_app(request: Request, exc: ErrorApp) -> JSONResponse:
    return _respuesta(exc.status_code, exc.code, exc.message, exc.headers)


async def manejar_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code, message = MENSAJES_HTTP.get(
        exc.status_code, ("error_http", "No se pudo procesar la solicitud.")
    )
    headers = dict(exc.headers) if exc.headers else None
    return _respuesta(exc.status_code, code, message, headers)


async def manejar_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    campos = sorted({".".join(str(p) for p in e["loc"][1:]) or "solicitud" for e in exc.errors()})
    return _respuesta(422, "datos_invalidos", "Datos inválidos en: " + ", ".join(campos))


async def manejar_base_de_datos(request: Request, exc: OperationalError) -> JSONResponse:
    logger.error("No se pudo conectar con la base de datos")
    return _respuesta(
        503,
        "base_de_datos_no_disponible",
        "La base de datos no está disponible. Intenta de nuevo en unos minutos.",
    )


async def manejar_inesperado(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return _respuesta(500, "error_interno", "Ocurrió un error interno. Intenta de nuevo más tarde.")


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorApp, manejar_error_app)
    app.add_exception_handler(StarletteHTTPException, manejar_http)
    app.add_exception_handler(RequestValidationError, manejar_validacion)
    app.add_exception_handler(OperationalError, manejar_base_de_datos)
    app.add_exception_handler(Exception, manejar_inesperado)
