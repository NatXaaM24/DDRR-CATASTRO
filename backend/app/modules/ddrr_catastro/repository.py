from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.ddrr_catastro.models import (
    SRID_ALMACENAMIENTO,
    SRID_METRICO_LOCAL,
    Partida,
    Predio,
)


class DdrrCatastroRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def existe_partida(self, matricula: str) -> bool:
        consulta = select(Partida.id).where(Partida.matricula == matricula)
        return self.db.scalar(consulta) is not None

    def existe_predio(self, codigo_catastral: str) -> bool:
        consulta = select(Predio.id).where(Predio.codigo_catastral == codigo_catastral)
        return self.db.scalar(consulta) is not None

    def agregar_partida(self, partida: Partida) -> Partida:
        self.db.add(partida)
        self.db.flush()
        return partida

    def agregar_predio(self, predio: Predio, wkt_metrico: str) -> Predio:
        """Guarda el predio; su polígono llega en la proyección métrica local
        y se almacena en SRID 4326 (R-BCK-7)."""
        predio.geometria = func.ST_Transform(
            func.ST_GeomFromText(wkt_metrico, SRID_METRICO_LOCAL), SRID_ALMACENAMIENTO
        )
        self.db.add(predio)
        self.db.flush()
        return predio
