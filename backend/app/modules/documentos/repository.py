from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.documentos.models import Documento


class DocumentoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_por_hash(self, hash_sha256: str) -> Documento | None:
        consulta = select(Documento).where(Documento.hash_sha256 == hash_sha256)
        return self.db.scalars(consulta).first()

    def crear(self, documento: Documento) -> Documento:
        self.db.add(documento)
        self.db.flush()
        return documento
