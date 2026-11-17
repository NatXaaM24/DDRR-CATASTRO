import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import ModeloBase


class TipoDocumento(enum.StrEnum):
    testimonio = "testimonio"
    folio_real = "folio_real"
    plano_catastral = "plano_catastral"
    certificado_catastral = "certificado_catastral"
    otro = "otro"


class EstadoDocumento(enum.StrEnum):
    subido = "subido"
    en_revision = "en_revision"
    revisado = "revisado"
    revision_manual = "revision_manual"  # R-IA-8


class Documento(ModeloBase):
    """Un PDF subido por un funcionario para su revisión."""

    __tablename__ = "documentos"

    tipo: Mapped[TipoDocumento] = mapped_column(Enum(TipoDocumento, name="tipo_documento"))
    nombre_original: Mapped[str] = mapped_column(String(255))
    # Ruta relativa al directorio de almacenamiento, nunca la del cliente.
    ruta: Mapped[str] = mapped_column(String(500), unique=True)
    # SHA-256 en hexadecimal (R-SEG-8): si cambia, el documento está alterado.
    # Único: el mismo PDF no se puede subir dos veces.
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tamano_bytes: Mapped[int] = mapped_column(BigInteger)
    estado: Mapped[EstadoDocumento] = mapped_column(
        Enum(EstadoDocumento, name="estado_documento"),
        default=EstadoDocumento.subido,
        server_default=EstadoDocumento.subido.value,
        index=True,
    )
    # RESTRICT: un usuario con documentos no se borra (se desactiva).
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), index=True
    )
