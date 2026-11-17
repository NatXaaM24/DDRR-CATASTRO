import hashlib
import uuid
from pathlib import Path, PurePath
from typing import BinaryIO

import pymupdf
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ArchivoDemasiadoGrande, ArchivoNoValido, DocumentoDuplicado
from app.modules.bitacora.service import BitacoraService
from app.modules.documentos.models import Documento, TipoDocumento
from app.modules.documentos.repository import DocumentoRepository

TAMANO_BLOQUE = 1024 * 1024
CABECERA_PDF = b"%PDF-"
CARPETA_DOCUMENTOS = "documentos"
INDICE_HASH = "ix_documentos_hash_sha256"


def _leer_con_limite(archivo: BinaryIO, max_bytes: int) -> tuple[bytes, str]:
    """Lee el archivo por bloques; corta si supera el límite. Devuelve datos y SHA-256."""
    hasher = hashlib.sha256()
    bloques: list[bytes] = []
    total = 0
    while bloque := archivo.read(TAMANO_BLOQUE):
        total += len(bloque)
        if total > max_bytes:
            raise ArchivoDemasiadoGrande(
                f"El archivo supera el tamaño máximo de {max_bytes // (1024 * 1024)} MB."
            )
        hasher.update(bloque)
        bloques.append(bloque)
    if total == 0:
        raise ArchivoNoValido("El archivo está vacío.")
    return b"".join(bloques), hasher.hexdigest()


def _validar_pdf(datos: bytes) -> None:
    """Valida el tipo real (R-SEG-7): cabecera PDF y que PyMuPDF lo pueda abrir."""
    if not datos.startswith(CABECERA_PDF):
        raise ArchivoNoValido()
    try:
        with pymupdf.open(stream=datos, filetype="pdf") as pdf:
            if not pdf.is_pdf or pdf.page_count == 0:
                raise ArchivoNoValido()
            if pdf.needs_pass:
                raise ArchivoNoValido("El PDF está protegido con contraseña.")
    except ArchivoNoValido:
        raise
    except Exception as exc:
        raise ArchivoNoValido() from exc


def _nombre_seguro(nombre: str | None) -> str:
    """Solo el nombre final, sin carpetas del cliente; únicamente para mostrarlo."""
    limpio = PurePath((nombre or "").replace("\\", "/")).name.strip()
    return (limpio or "documento.pdf")[:255]


def _es_hash_duplicado(exc: IntegrityError) -> bool:
    diag = getattr(exc.orig, "diag", None)
    return getattr(diag, "constraint_name", None) == INDICE_HASH


class DocumentoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DocumentoRepository(db)
        self.bitacora = BitacoraService(db)

    def subir_documento(
        self,
        archivo: BinaryIO,
        nombre_original: str | None,
        tipo: TipoDocumento,
        *,
        usuario_id: uuid.UUID,
    ) -> Documento:
        settings = get_settings()
        datos, hash_sha256 = _leer_con_limite(archivo, settings.max_upload_mb * 1024 * 1024)
        _validar_pdf(datos)

        # Aviso temprano; la restricción UNIQUE cubre las subidas simultáneas.
        if self.repo.obtener_por_hash(hash_sha256) is not None:
            raise DocumentoDuplicado()

        documento_id = uuid.uuid4()
        ruta = f"{CARPETA_DOCUMENTOS}/{documento_id}.pdf"
        destino = settings.storage_dir / ruta
        self._guardar(destino, datos)

        try:
            documento = self.repo.crear(
                Documento(
                    id=documento_id,
                    tipo=tipo,
                    nombre_original=_nombre_seguro(nombre_original),
                    ruta=ruta,
                    hash_sha256=hash_sha256,
                    tamano_bytes=len(datos),
                    usuario_id=usuario_id,
                )
            )
            self.bitacora.registrar(
                "documento_subido",
                "documento",
                usuario_id=usuario_id,
                entidad_id=documento.id,
                detalle={"tipo": tipo.value, "tamano_bytes": len(datos)},
            )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            destino.unlink(missing_ok=True)
            if _es_hash_duplicado(exc):
                raise DocumentoDuplicado() from exc
            raise
        except Exception:
            self.db.rollback()
            destino.unlink(missing_ok=True)
            raise
        return documento

    @staticmethod
    def _guardar(destino: Path, datos: bytes) -> None:
        """Escribe en un temporal y lo renombra: nunca queda un PDF a medias."""
        destino.parent.mkdir(parents=True, exist_ok=True)
        temporal = destino.with_suffix(".parcial")
        try:
            temporal.write_bytes(datos)
            temporal.replace(destino)
        except Exception:
            temporal.unlink(missing_ok=True)
            raise
