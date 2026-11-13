from typing import Annotated

from fastapi import APIRouter, Cookie, Response

from app.core.config import get_settings
from app.core.db import DbSession
from app.modules.auth.dependencies import CualquierRol
from app.modules.auth.schemas import LoginRequest, TokenSalida, UsuarioSalida
from app.modules.auth.service import AuthService

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


@router.post("/login", response_model=TokenSalida)
def login(datos: LoginRequest, response: Response, db: DbSession) -> TokenSalida:
    servicio = AuthService(db)
    usuario = servicio.autenticar(datos.username, datos.password)
    acceso, refresh = servicio.emitir_tokens(usuario)
    _poner_cookie(response, refresh)
    return _respuesta_tokens(UsuarioSalida.model_validate(usuario), acceso)


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
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_REFRESH, path=RUTA_COOKIE)


@router.get("/me", response_model=UsuarioSalida)
def me(usuario: CualquierRol) -> UsuarioSalida:
    return UsuarioSalida.model_validate(usuario)
