import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.core.db import DbSession
from app.core.paginacion import Pagina, ParametrosPagina
from app.modules.auth.dependencies import CualquierRol, SoloFuncionario
from app.modules.documentos.models import EstadoDocumento, TipoDocumento
from app.modules.documentos.schemas import DocumentoSalida
from app.modules.documentos.service import DocumentoService

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.post("", response_model=DocumentoSalida, status_code=201)
def subir(
    archivo: Annotated[UploadFile, File()],
    tipo: Annotated[TipoDocumento, Form()],
    funcionario: SoloFuncionario,
    db: DbSession,
) -> DocumentoSalida:
    documento = DocumentoService(db).subir_documento(
        archivo.file, archivo.filename, tipo, usuario_id=funcionario.id
    )
    return DocumentoSalida.model_validate(documento)


@router.get("", response_model=Pagina[DocumentoSalida])
def listar(
    usuario: CualquierRol,
    db: DbSession,
    paginacion: ParametrosPagina,
    estado: EstadoDocumento | None = None,
    tipo: TipoDocumento | None = None,
) -> Pagina[DocumentoSalida]:
    documentos, total = DocumentoService(db).listar(
        usuario,
        estado=estado,
        tipo=tipo,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
    return Pagina(
        items=[DocumentoSalida.model_validate(d) for d in documentos],
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.get("/{documento_id}", response_model=DocumentoSalida)
def ver(documento_id: uuid.UUID, usuario: CualquierRol, db: DbSession) -> DocumentoSalida:
    return DocumentoSalida.model_validate(DocumentoService(db).obtener(documento_id, usuario))


@router.get("/{documento_id}/pdf", response_class=FileResponse)
def servir_pdf(documento_id: uuid.UUID, usuario: CualquierRol, db: DbSession) -> FileResponse:
    ruta, documento = DocumentoService(db).abrir_pdf(documento_id, usuario)
    return FileResponse(
        ruta,
        media_type="application/pdf",
        filename=documento.nombre_original,
        content_disposition_type="inline",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )
