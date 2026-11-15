from typing import Annotated

from fastapi import APIRouter, Cookie, Request, Response

from app.core.config import get_settings
from app.core.db import DbSession
from app.modules.auth.dependencies import CualquierRol, UsuarioPreauth
from app.modules.auth.schemas import (
    LoginRequest,
    LoginSalida,
    TokenSalida,
    UsuarioSalida,
    WebAuthnAutenticacionRequest,
    WebAuthnRegistroRequest,
)
from app.modules.auth.service import AuthService
from app.modules.auth.webauthn_service import WebAuthnService
from app.modules.funcionarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])

COOKIE_REFRESH = "refresh_token"
RUTA_COOKIE = "/api/v1/auth"  # la cookie solo viaja a los endpoints de auth


def _poner_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=COOKIE_REFRESH,
        value=refresh_token,
        max_age=settings.refresh_token_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path=RUTA_COOKIE,
    )


def _respuesta_tokens(usuario: UsuarioSalida, acceso: str) -> TokenSalida:
    return TokenSalida(
        access_token=acceso,
        expires_in=get_settings().access_token_minutes * 60,
        usuario=usuario,
    )


def _completar_sesion(usuario: Usuario, response: Response, db: DbSession) -> TokenSalida:
    """Se llama solo cuando contraseña y biometría ya fueron verificadas."""
    acceso, refresh = AuthService(db).emitir_tokens(usuario)
    _poner_cookie(response, refresh)
    return _respuesta_tokens(UsuarioSalida.model_validate(usuario), acceso)


# ---------- Paso 1: contraseña ----------


@router.post("/login", response_model=LoginSalida)
def login(datos: LoginRequest, request: Request, db: DbSession) -> LoginSalida:
    ip = request.client.host if request.client else "desconocida"
    preauth, tiene_credencial = AuthService(db).iniciar_login(datos.username, datos.password, ip)
    return LoginSalida(
        preauth_token=preauth,
        expires_in=get_settings().preauth_minutes * 60,
        tiene_credencial=tiene_credencial,
    )


# ---------- Paso 2: biometría (WebAuthn) ----------


@router.post("/webauthn/registro/opciones")
def registro_opciones(usuario: UsuarioPreauth, db: DbSession) -> Response:
    opciones = WebAuthnService(db).opciones_registro(usuario)
    return Response(content=opciones, media_type="application/json")


@router.post("/webauthn/registro/verificar", response_model=TokenSalida)
def registro_verificar(
    datos: WebAuthnRegistroRequest,
    usuario: UsuarioPreauth,
    response: Response,
    db: DbSession,
) -> TokenSalida:
    WebAuthnService(db).verificar_registro(usuario, datos.credencial, datos.nombre)
    return _completar_sesion(usuario, response, db)


@router.post("/webauthn/autenticacion/opciones")
def autenticacion_opciones(usuario: UsuarioPreauth, db: DbSession) -> Response:
    opciones = WebAuthnService(db).opciones_autenticacion(usuario)
    return Response(content=opciones, media_type="application/json")


@router.post("/webauthn/autenticacion/verificar", response_model=TokenSalida)
def autenticacion_verificar(
    datos: WebAuthnAutenticacionRequest,
    usuario: UsuarioPreauth,
    response: Response,
    db: DbSession,
) -> TokenSalida:
    WebAuthnService(db).verificar_autenticacion(usuario, datos.credencial)
    return _completar_sesion(usuario, response, db)


# ---------- Sesión ----------


@router.post("/refresh", response_model=TokenSalida)
def refresh(
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenSalida:
    usuario, acceso, nuevo_refresh = AuthService(db).refrescar(refresh_token)
    _poner_cookie(response, nuevo_refresh)
    return _respuesta_tokens(UsuarioSalida.model_validate(usuario), acceso)


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    AuthService(db).cerrar_sesion(refresh_token)
    response.delete_cookie(COOKIE_REFRESH, path=RUTA_COOKIE)


@router.get("/me", response_model=UsuarioSalida)
def me(usuario: CualquierRol) -> UsuarioSalida:
    return UsuarioSalida.model_validate(usuario)
