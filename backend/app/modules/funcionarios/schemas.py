import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.funcionarios.models import Rol


class FuncionarioCrear(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-z0-9._-]+$")
    nombre_completo: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=10, max_length=128)
    rol: Rol


class FuncionarioEditar(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que se envía."""

    nombre_completo: str | None = Field(default=None, min_length=1, max_length=150)
    rol: Rol | None = None
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=10, max_length=128)


class FuncionarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    nombre_completo: str
    rol: Rol
    activo: bool
    created_at: datetime
