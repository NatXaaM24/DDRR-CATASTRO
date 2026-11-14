import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.funcionarios.models import Rol


class LoginRequest(BaseModel):
    username: str
    password: str


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    nombre_completo: str
    rol: Rol


class LoginSalida(BaseModel):
    """Respuesta del paso 1: todavía no hay sesión, falta la biometría."""

    preauth_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    tiene_credencial: bool


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    usuario: UsuarioSalida


class WebAuthnRegistroRequest(BaseModel):
    credencial: dict[str, Any]
    nombre: str = Field(default="Dispositivo", min_length=1, max_length=100)


class WebAuthnAutenticacionRequest(BaseModel):
    credencial: dict[str, Any]
