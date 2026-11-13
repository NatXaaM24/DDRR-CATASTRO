from sqlalchemy.orm import Session

from app.core.errors import NoAutenticado
from app.core.security import hash_password, verify_password
from app.modules.funcionarios.models import Usuario
from app.modules.funcionarios.service import FuncionarioService

_HASH_FALSO = hash_password("relleno-no-usar")


class AuthService:
    def __init__(self, db: Session) -> None:
        self.funcionarios = FuncionarioService(db)

    def autenticar(self, username: str, password: str) -> Usuario:
        usuario = self.funcionarios.obtener_por_username(username)
        hash_a_comparar = usuario.password_hash if usuario else _HASH_FALSO
        password_correcta = verify_password(password, hash_a_comparar)

        if usuario is None or not password_correcta or not usuario.activo:
            raise NoAutenticado("Usuario o contraseña incorrectos.")
        return usuario
