import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.documentos.models import EstadoDocumento, TipoDocumento


class DocumentoSalida(BaseModel):
    """Datos públicos de un documento. La ruta en disco nunca sale de la API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: TipoDocumento
    nombre_original: str
    hash_sha256: str
    tamano_bytes: int
    estado: EstadoDocumento
    usuario_id: uuid.UUID
    created_at: datetime
