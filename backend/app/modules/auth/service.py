import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import NoAutenticado
from app.core.security import (
    TIPO_ACCESO,
    TIPO_PREAUTH,
    TIPO_REFRESH,
    crear_token,
    decodificar_token,
    hash_password,
    verify_password,
)
from app.modules.auth.webauthn_service import WebAuthnService
from app.modules.funcionarios.models import Usuario
from app.modules.funcionarios.service import FuncionarioService

# Hash de relleno: si el usuario no existe, igual verificamos contra este hash
# para que la respuesta tarde lo mismo y no se pueda adivinar qué usuarios existen.
_HASH_FALSO = hash_password("relleno-no-usar")


class AuthService:
    def __init__(self, db: Session) -> None:
        self.funcionarios = FuncionarioService(db)
        self.webauthn = WebAuthnService(db)

    def autenticar(self, username: str, password: str) -> Usuario:
        usuario = self.funcionarios.obtener_por_username(username)
        hash_a_comparar = usuario.password_hash if usuario else _HASH_FALSO
        password_correcta = verify_password(password, hash_a_comparar)

        if usuario is None or not password_correcta or not usuario.activo:
            raise NoAutenticado("Usuario o contraseña incorrectos.")
        return usuario

    def iniciar_login(self, username: str, password: str) -> tuple[str, bool]:
        """Paso 1: valida la contraseña. Devuelve (preauth_token, tiene_credencial)."""
        usuario = self.autenticar(username, password)
        preauth = crear_token(
            str(usuario.id),
            TIPO_PREAUTH,
            timedelta(minutes=get_settings().preauth_minutes),
        )
        return preauth, self.webauthn.tiene_credencial(usuario)

    def emitir_tokens(self, usuario: Usuario) -> tuple[str, str]:
        """Paso 2 (tras WebAuthn): devuelve (token_de_acceso, refresh_token)."""
        settings = get_settings()
        acceso = crear_token(
            str(usuario.id), TIPO_ACCESO, timedelta(minutes=settings.access_token_minutes)
        )
        refresh = crear_token(
            str(usuario.id), TIPO_REFRESH, timedelta(days=settings.refresh_token_days)
        )
        return acceso, refresh

    def _usuario_desde_token(self, token: str | None, tipo: str) -> Usuario:
        if not token:
            raise NoAutenticado()
        sub = decodificar_token(token, tipo)
        try:
            usuario_id = uuid.UUID(sub)
        except ValueError:
            raise NoAutenticado() from None
        usuario = self.funcionarios.obtener_por_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise NoAutenticado()
        return usuario

    def usuario_desde_acceso(self, token: str | None) -> Usuario:
        return self._usuario_desde_token(token, TIPO_ACCESO)

    def usuario_desde_preauth(self, token: str | None) -> Usuario:
        return self._usuario_desde_token(token, TIPO_PREAUTH)

    def refrescar(self, refresh_token: str | None) -> tuple[Usuario, str, str]:
        usuario = self._usuario_desde_token(refresh_token, TIPO_REFRESH)
        acceso, nuevo_refresh = self.emitir_tokens(usuario)
        return usuario, acceso, nuevo_refresh
