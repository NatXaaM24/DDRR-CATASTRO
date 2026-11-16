import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.funcionarios.models import Rol, Usuario


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

    def obtener_por_id(self, usuario_id: uuid.UUID) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def listar(
        self,
        *,
        rol: Rol | None,
        activo: bool | None,
        buscar: str | None,
        limite: int,
        offset: int,
    ) -> tuple[list[Usuario], int]:
        filtros = []
        if rol is not None:
            filtros.append(Usuario.rol == rol)
        if activo is not None:
            filtros.append(Usuario.activo == activo)
        if buscar:
            # Se escapan % y _ para que el texto buscado se tome literal.
            escapado = buscar.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            patron = f"%{escapado}%"
            filtros.append(
                or_(
                    Usuario.username.ilike(patron, escape="\\"),
                    Usuario.nombre_completo.ilike(patron, escape="\\"),
                )
            )

        total = self.db.scalar(select(func.count()).select_from(Usuario).where(*filtros)) or 0
        consulta = (
            select(Usuario)
            .where(*filtros)
            .order_by(Usuario.nombre_completo, Usuario.id)
            .limit(limite)
            .offset(offset)
        )
        return list(self.db.scalars(consulta)), total
