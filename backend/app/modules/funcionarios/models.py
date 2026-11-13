import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import ModeloBase


class Rol(str, enum.Enum):
    funcionario = "funcionario"
    encargado = "encargado"


class Usuario(ModeloBase):
    __tablename__ = "usuarios"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[Rol] = mapped_column(Enum(Rol, name="rol_usuario"))
    activo: Mapped[bool] = mapped_column(default=True)
