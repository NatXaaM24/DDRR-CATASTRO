import uuid
from datetime import datetime

from fastapi import APIRouter

from app.core.db import DbSession
from app.core.paginacion import Pagina, ParametrosPagina
from app.modules.auth.dependencies import SoloEncargado
from app.modules.bitacora.schemas import BitacoraSalida
from app.modules.bitacora.service import BitacoraService

router = APIRouter(prefix="/bitacora", tags=["Bitácora"])


@router.get("", response_model=Pagina[BitacoraSalida])
def consultar(
    encargado: SoloEncargado,
    db: DbSession,
    paginacion: ParametrosPagina,
    usuario_id: uuid.UUID | None = None,
    accion: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> Pagina[BitacoraSalida]:
    registros, total = BitacoraService(db).listar(
        usuario_id=usuario_id,
        accion=accion,
        desde=desde,
        hasta=hasta,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
    return Pagina(
        items=[BitacoraSalida.model_validate(r) for r in registros],
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
