from sqlalchemy.orm import Session

from app.modules.ddrr_catastro.models import Partida, Predio
from app.modules.ddrr_catastro.repository import DdrrCatastroRepository


class DdrrCatastroService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DdrrCatastroRepository(db)

    def cargar_datos_simulados(
        self, partidas: list[Partida], predios: list[tuple[Predio, str]]
    ) -> tuple[int, int]:
        """Carga los datos simulados de DDRR y Catastro (T-4.3).

        Es idempotente: omite las partidas y los predios que ya existen.
        `predios` son pares (predio, polígono WKT en la proyección métrica local).
        Devuelve cuántas partidas y cuántos predios se insertaron.
        """
        nuevas_partidas = 0
        for partida in partidas:
            if not self.repo.existe_partida(partida.matricula):
                self.repo.agregar_partida(partida)
                nuevas_partidas += 1

        nuevos_predios = 0
        for predio, wkt_metrico in predios:
            if not self.repo.existe_predio(predio.codigo_catastral):
                self.repo.agregar_predio(predio, wkt_metrico)
                nuevos_predios += 1

        self.db.commit()
        return nuevas_partidas, nuevos_predios
