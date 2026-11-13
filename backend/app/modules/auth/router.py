from fastapi import APIRouter

from app.core.db import DbSession
from app.modules.auth.schemas import LoginRequest, UsuarioSalida
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UsuarioSalida)
def login(datos: LoginRequest, db: DbSession) -> UsuarioSalida:
    usuario = AuthService(db).autenticar(datos.username, datos.password)
    return UsuarioSalida.model_validate(usuario)
