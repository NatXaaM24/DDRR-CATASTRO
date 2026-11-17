import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.documentos.models import Documento, EstadoDocumento, TipoDocumento


class DocumentoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_por_id(self, documento_id: uuid.UUID) -> Documento | None:
        return self.db.get(Documento, documento_id)

    def obtener_por_hash(self, hash_sha256: str) -> Documento | None:
        consulta = select(Documento).where(Documento.hash_sha256 == hash_sha256)
        return self.db.scalars(consulta).first()

    def crear(self, documento: Documento) -> Documento:
        self.db.add(documento)
        self.db.flush()
        return documento

    def listar(
        self,
        *,
        usuario_id: uuid.UUID | None,
        estado: EstadoDocumento | None,
        tipo: TipoDocumento | None,
        limite: int,
        offset: int,
    ) -> tuple[list[Documento], int]:
        filtros = []
        if usuario_id is not None:
            filtros.append(Documento.usuario_id == usuario_id)
        if estado is not None:
            filtros.append(Documento.estado == estado)
        if tipo is not None:
            filtros.append(Documento.tipo == tipo)

        total = self.db.scalar(select(func.count()).select_from(Documento).where(*filtros)) or 0
        consulta = (
            select(Documento)
            .where(*filtros)
            .order_by(Documento.created_at.desc(), Documento.id)
            .limit(limite)
            .offset(offset)
        )
        return list(self.db.scalars(consulta)), total
