from sqlalchemy.orm import Session

from app.core.errors import Conflicto
from app.core.security import hash_password
from app.modules.funcionarios.models import Rol, Usuario
from app.modules.funcionarios.repository import UsuarioRepository


class FuncionarioService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UsuarioRepository(db)

    def obtener_por_username(self, username: str) -> Usuario | None:
        return self.repo.obtener_por_username(username)

    def crear_usuario(
        self, username: str, nombre_completo: str, password: str, rol: Rol
    ) -> Usuario:
        if self.repo.obtener_por_username(username):
            raise Conflicto("El nombre de usuario ya existe.")
        usuario = Usuario(
            username=username,
            nombre_completo=nombre_completo,
            password_hash=hash_password(password),
            rol=rol,
        )
        self.repo.crear(usuario)
        self.db.commit()
        return usuario
