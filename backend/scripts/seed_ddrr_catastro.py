"""Datos simulados de DDRR y Catastro (T-4.3).

Uso: uv run python -m scripts.seed_ddrr_catastro

Crea predios rectangulares en el centro de Cochabamba. Las medidas se dan en
metros sobre la proyección métrica local (UTM 19S) y se guardan en SRID 4326.
Es idempotente: se puede ejecutar varias veces.

Casos coherentes: 01 a 06 (partida y predio coinciden en todo).
Casos con discrepancias deliberadas:
  07  superficie distinta entre DDRR (320 m²) y Catastro (300 m²)
  08  titular distinto (venta inscrita en DDRR, no actualizada en Catastro)
  09  CI del titular distinto (error de digitación)
  10  dirección distinta
  11  la partida cita un código catastral que no existe en Catastro
  12  predio de Catastro sin partida en DDRR
  13  la superficie declarada en Catastro no coincide con el área del polígono
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.core.db import SessionLocal
from app.modules.ddrr_catastro.models import Partida, Predio
from app.modules.ddrr_catastro.service import DdrrCatastroService

# Punto de referencia en UTM 19S, cerca de la plaza 14 de Septiembre.
ESTE_BASE = 802_100.0
NORTE_BASE = 8_074_670.0


@dataclass
class Caso:
    numero: int
    titular: str
    ci: str
    direccion: str
    distrito: str
    ancho_m: float
    largo_m: float


def rectangulo_wkt(numero: int, ancho: float, largo: float) -> str:
    """Rectángulo en UTM 19S; cada caso ocupa su propia celda de una cuadrícula."""
    x0 = ESTE_BASE + ((numero - 1) % 5) * 60
    y0 = NORTE_BASE + ((numero - 1) // 5) * 60
    x1, y1 = x0 + ancho, y0 + largo
    return f"POLYGON(({x0} {y0}, {x1} {y0}, {x1} {y1}, {x0} {y1}, {x0} {y0}))"


def matricula(numero: int) -> str:
    return f"3.01.1.01.{numero:07d}"


def codigo(numero: int) -> str:
    return f"01-010-{numero:03d}-0001"


CASOS = [
    Caso(1, "Juan Carlos Mamani Quispe", "4512367", "Calle Jordán N° 245", "D-10", 12, 25),
    Caso(2, "María Elena Rojas Vargas", "5823104", "Av. Heroínas N° 580", "D-10", 15, 20),
    Caso(3, "Luis Fernando Gutiérrez Soria", "3901225", "Calle España N° 312", "D-10", 10, 30),
    Caso(4, "Ana Lucía Choque Flores", "6214578", "Calle Sucre N° 1020", "D-10", 18, 22),
    Caso(5, "Roberto Andrés Céspedes Lara", "4478921", "Av. Ayacucho N° 455", "D-10", 14, 28),
    Caso(6, "Silvia Patricia Torrico Ríos", "5390012", "Calle Baptista N° 760", "D-10", 16, 25),
    Caso(7, "Jorge Luis Fernández Arce", "3765490", "Calle Esteban Arce N° 150", "D-10", 12, 25),
    Caso(8, "Carmen Rosa Villarroel Paz", "4120983", "Calle Antezana N° 890", "D-10", 15, 18),
    Caso(9, "Pedro Pablo Zurita Montaño", "5067821", "Calle 25 de Mayo N° 330", "D-10", 11, 27),
    Caso(10, "Gabriela Inés Salazar Soto", "6638410", "Av. San Martín N° 640", "D-10", 13, 24),
    Caso(11, "Hugo Ernesto Arnez Camacho", "3982107", "Calle Lanza N° 520", "D-10", 10, 20),
    Caso(12, "Rosa Amalia Quiroga Delgadillo", "4875230", "Calle Tarata N° 210", "D-10", 12, 20),
    Caso(13, "Marco Antonio Ledezma Vera", "5501736", "Calle Uruguay N° 415", "D-10", 15, 20),
]


def construir() -> tuple[list[Partida], list[tuple[Predio, str]]]:
    partidas: list[Partida] = []
    predios: list[tuple[Predio, str]] = []

    for caso in CASOS:
        area = Decimal(str(caso.ancho_m * caso.largo_m)).quantize(Decimal("0.01"))

        partida = Partida(
            matricula=matricula(caso.numero),
            titular_nombre=caso.titular,
            titular_ci=caso.ci,
            superficie_m2=area,
            direccion=caso.direccion,
            codigo_catastral=codigo(caso.numero),
            fecha_inscripcion=date(2015 + caso.numero % 10, 1 + caso.numero % 12, 10),
        )
        predio = Predio(
            codigo_catastral=codigo(caso.numero),
            propietario_nombre=caso.titular,
            propietario_ci=caso.ci,
            superficie_m2=area,
            direccion=caso.direccion,
            distrito=caso.distrito,
        )

        # Discrepancias deliberadas.
        match caso.numero:
            case 7:
                partida.superficie_m2 = Decimal("320.00")
            case 8:
                predio.propietario_nombre = "Teodoro Villarroel Ugarte"
                predio.propietario_ci = "2984471"
            case 9:
                predio.propietario_ci = "5067812"
            case 10:
                predio.direccion = "Av. San Martín N° 664"
            case 11:
                partida.codigo_catastral = "01-010-999-0001"
            case 13:
                predio.superficie_m2 = Decimal("350.00")

        if caso.numero != 12:
            partidas.append(partida)
        predios.append((predio, rectangulo_wkt(caso.numero, caso.ancho_m, caso.largo_m)))

    return partidas, predios


def main() -> None:
    partidas, predios = construir()
    with SessionLocal() as db:
        n_partidas, n_predios = DdrrCatastroService(db).cargar_datos_simulados(partidas, predios)
    print(f"Partidas nuevas: {n_partidas}. Predios nuevos: {n_predios}.")


if __name__ == "__main__":
    main()
