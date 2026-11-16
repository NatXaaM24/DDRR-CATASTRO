import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.bitacora.models import Bitacora


class BitacoraRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, registro: Bitacora) -> None:
        self.db.add(registro)
        self.db.flush()

    def listar(
        self,
        *,
        usuario_id: uuid.UUID | None,
        accion: str | None,
        desde: datetime | None,
        hasta: datetime | None,
        limite: int,
        offset: int,
    ) -> tuple[list[Bitacora], int]:
        filtros = []
        if usuario_id is not None:
            filtros.append(Bitacora.usuario_id == usuario_id)
        if accion is not None:
            filtros.append(Bitacora.accion == accion)
        if desde is not None:
            filtros.append(Bitacora.created_at >= desde)
        if hasta is not None:
            filtros.append(Bitacora.created_at <= hasta)

        total = self.db.scalar(select(func.count()).select_from(Bitacora).where(*filtros)) or 0
        consulta = (
            select(Bitacora)
            .where(*filtros)
            .order_by(Bitacora.created_at.desc(), Bitacora.id.desc())
            .limit(limite)
            .offset(offset)
        )
        return list(self.db.scalars(consulta)), total
