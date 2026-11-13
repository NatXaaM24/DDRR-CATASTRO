from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.funcionarios.models import Usuario


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_por_username(self, username: str) -> Usuario | None:
        consulta = select(Usuario).where(Usuario.username == username)
        return self.db.scalars(consulta).first()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.flush()
        return usuario
