from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.core.db import DbSession
from app.modules.auth.dependencies import SoloFuncionario
from app.modules.documentos.models import TipoDocumento
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
