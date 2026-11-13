from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.db import DbSession
from app.core.errors import NoAutenticado, SinPermiso
from app.modules.auth.service import AuthService
from app.modules.funcionarios.models import Rol, Usuario

_bearer = HTTPBearer(auto_error=False)


def usuario_actual(
    db: DbSession,
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Usuario:
    if credenciales is None:
        raise NoAutenticado()
    return AuthService(db).usuario_desde_acceso(credenciales.credentials)


UsuarioActual = Annotated[Usuario, Depends(usuario_actual)]


def requiere_rol(*roles: Rol) -> Callable[[Usuario], Usuario]:
    """Crea una dependencia que solo deja pasar a los roles indicados."""

    def verificar(usuario: UsuarioActual) -> Usuario:
        if usuario.rol not in roles:
            raise SinPermiso()
        return usuario

    return verificar


# Atajos para declarar el rol en cada endpoint (R-SEG-1):
CualquierRol = Annotated[Usuario, Depends(requiere_rol(Rol.funcionario, Rol.encargado))]
SoloEncargado = Annotated[Usuario, Depends(requiere_rol(Rol.encargado))]
SoloFuncionario = Annotated[Usuario, Depends(requiere_rol(Rol.funcionario))]
