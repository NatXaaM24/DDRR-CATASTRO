import uuid

from pydantic import BaseModel, ConfigDict

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
