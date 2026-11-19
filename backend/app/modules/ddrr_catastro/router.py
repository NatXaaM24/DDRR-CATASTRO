from fastapi import APIRouter

from app.core.db import DbSession
from app.modules.auth.dependencies import CualquierRol
from app.modules.ddrr_catastro.schemas import PartidaSalida, PredioSalida
from app.modules.ddrr_catastro.service import DdrrCatastroService

router = APIRouter(prefix="/ddrr-catastro", tags=["DDRR y Catastro"])


@router.get("/partidas/{matricula}", response_model=PartidaSalida)
def obtener_partida(matricula: str, _usuario: CualquierRol, db: DbSession) -> PartidaSalida:
    return DdrrCatastroService(db).obtener_partida(matricula)


@router.get("/predios/{codigo_catastral}", response_model=PredioSalida)
def obtener_predio(codigo_catastral: str, _usuario: CualquierRol, db: DbSession) -> PredioSalida:
    return DdrrCatastroService(db).obtener_predio(codigo_catastral)
