import json

from sqlalchemy.orm import Session

from app.core.errors import NoEncontrado
from app.modules.ddrr_catastro.models import Partida, Predio
from app.modules.ddrr_catastro.repository import DdrrCatastroRepository
from app.modules.ddrr_catastro.schemas import PartidaSalida, PredioSalida


class DdrrCatastroService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DdrrCatastroRepository(db)

    def obtener_partida(self, matricula: str) -> PartidaSalida:
        partida = self.repo.obtener_partida(matricula)
        if partida is None:
            raise NoEncontrado("No se encontró la partida en DDRR.")
        return PartidaSalida.model_validate(partida)

    def obtener_predio(self, codigo_catastral: str) -> PredioSalida:
        resultado = self.repo.obtener_predio(codigo_catastral)
        if resultado is None:
            raise NoEncontrado("No se encontró el predio en Catastro.")
        predio, geojson = resultado
        return PredioSalida(
            id=predio.id,
            codigo_catastral=predio.codigo_catastral,
            propietario_nombre=predio.propietario_nombre,
            propietario_ci=predio.propietario_ci,
            superficie_m2=predio.superficie_m2,
            direccion=predio.direccion,
            distrito=predio.distrito,
            geometria=json.loads(geojson),
        )

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
