"""Pruebas de las consultas de DDRR y Catastro (T-4.5)."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import delete, func, select

from app.core.db import SessionLocal
from app.core.errors import NoEncontrado
from app.modules.ddrr_catastro.models import SRID_METRICO_LOCAL, Partida, Predio
from app.modules.ddrr_catastro.service import DdrrCatastroService
from scripts import seed_ddrr_catastro

URL = "/api/v1/ddrr-catastro"

# Rectángulo de 12 m x 25 m (300 m²) en UTM 19S, en el centro de Cochabamba.
X0, Y0 = 802_100.0, 8_074_670.0
X1, Y1 = X0 + 12, Y0 + 25
POLIGONO_300 = f"POLYGON(({X0} {Y0}, {X1} {Y0}, {X1} {Y1}, {X0} {Y1}, {X0} {Y0}))"


@pytest.fixture
def datos():
    """Partida y predio propios de la prueba, con identificadores únicos; al terminar se borran."""
    sufijo = uuid.uuid4().hex[:8]
    matricula = f"T.{sufijo}"
    codigo = f"T-{sufijo}"
    partida = Partida(
        matricula=matricula,
        titular_nombre="Titular de Prueba",
        titular_ci="1234567",
        superficie_m2=Decimal("300.00"),
        direccion="Calle de Prueba N° 1",
        codigo_catastral=codigo,
        fecha_inscripcion=date(2020, 5, 10),
    )
    predio = Predio(
        codigo_catastral=codigo,
        propietario_nombre="Titular de Prueba",
        propietario_ci="1234567",
        superficie_m2=Decimal("300.00"),
        direccion="Calle de Prueba N° 1",
        distrito="D-10",
    )
    with SessionLocal() as db:
        DdrrCatastroService(db).cargar_datos_simulados([partida], [(predio, POLIGONO_300)])
    yield matricula, codigo
    with SessionLocal() as db:
        db.execute(delete(Partida).where(Partida.matricula == matricula))
        db.execute(delete(Predio).where(Predio.codigo_catastral == codigo))
        db.commit()


# ---------- Servicio ----------


def test_servicio_obtiene_partida(datos):
    matricula, codigo = datos
    with SessionLocal() as db:
        partida = DdrrCatastroService(db).obtener_partida(matricula)
    assert partida.matricula == matricula
    assert partida.codigo_catastral == codigo
    assert partida.titular_ci == "1234567"
    assert partida.superficie_m2 == Decimal("300.00")
    assert partida.fecha_inscripcion == date(2020, 5, 10)


def test_servicio_obtiene_predio_con_geojson(datos):
    _, codigo = datos
    with SessionLocal() as db:
        predio = DdrrCatastroService(db).obtener_predio(codigo)
    assert predio.codigo_catastral == codigo
    assert predio.geometria["type"] == "Polygon"
    anillo = predio.geometria["coordinates"][0]
    assert anillo[0] == anillo[-1]  # anillo cerrado
    # Guardado en 4326: longitudes y latitudes de Cochabamba, no metros.
    for lon, lat in anillo:
        assert -66.3 < lon < -66.0
        assert -17.5 < lat < -17.3


def test_servicio_partida_inexistente():
    with SessionLocal() as db, pytest.raises(NoEncontrado):
        DdrrCatastroService(db).obtener_partida("no-existe")


def test_servicio_predio_inexistente():
    with SessionLocal() as db, pytest.raises(NoEncontrado):
        DdrrCatastroService(db).obtener_predio("no-existe")


def test_carga_simulada_es_idempotente(datos):
    matricula, codigo = datos
    repetida = Partida(
        matricula=matricula,
        titular_nombre="Otro",
        titular_ci="0",
        superficie_m2=Decimal("1"),
        direccion="Otra",
        codigo_catastral=codigo,
        fecha_inscripcion=date(2021, 1, 1),
    )
    with SessionLocal() as db:
        nuevas = DdrrCatastroService(db).cargar_datos_simulados([repetida], [])
        assert nuevas == (0, 0)
        assert DdrrCatastroService(db).obtener_partida(matricula).titular_nombre == (
            "Titular de Prueba"
        )


# ---------- Espacial ----------


def test_poligono_en_4326_y_area_en_proyeccion_metrica(datos):
    _, codigo = datos
    with SessionLocal() as db:
        srid, area = db.execute(
            select(
                func.ST_SRID(Predio.geometria),
                func.ST_Area(func.ST_Transform(Predio.geometria, SRID_METRICO_LOCAL)),
            ).where(Predio.codigo_catastral == codigo)
        ).one()
    assert srid == 4326
    assert area == pytest.approx(300, abs=0.5)


# ---------- Endpoints ----------


def test_endpoint_partida_funcionario(cliente, h_funcionario, datos):
    matricula, codigo = datos
    r = cliente.get(f"{URL}/partidas/{matricula}", headers=h_funcionario)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["matricula"] == matricula
    assert cuerpo["codigo_catastral"] == codigo
    assert cuerpo["superficie_m2"] == "300.00"


def test_endpoint_predio_encargado(cliente, h_encargado, datos):
    _, codigo = datos
    r = cliente.get(f"{URL}/predios/{codigo}", headers=h_encargado)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["codigo_catastral"] == codigo
    assert cuerpo["geometria"]["type"] == "Polygon"


@pytest.mark.parametrize("ruta", ["partidas", "predios"])
def test_endpoint_inexistente_404(cliente, h_funcionario, ruta):
    r = cliente.get(f"{URL}/{ruta}/no-existe", headers=h_funcionario)
    assert r.status_code == 404
    assert r.json()["code"] == "no_encontrado"
    assert "message" in r.json()


@pytest.mark.parametrize("ruta", ["partidas", "predios"])
def test_endpoint_sin_token_401(cliente, datos, ruta):
    matricula, codigo = datos
    identificador = matricula if ruta == "partidas" else codigo
    r = cliente.get(f"{URL}/{ruta}/{identificador}")
    assert r.status_code == 401


# ---------- Datos simulados (seed) ----------


def test_seed_tiene_casos_coherentes_y_discrepancias():
    partidas, predios = seed_ddrr_catastro.construir()
    por_codigo = {predio.codigo_catastral: predio for predio, _ in predios}
    por_matricula = {p.matricula: p for p in partidas}

    def par(numero: int) -> tuple[Partida, Predio]:
        partida = por_matricula[seed_ddrr_catastro.matricula(numero)]
        return partida, por_codigo[seed_ddrr_catastro.codigo(numero)]

    # 01: coherente.
    partida, predio = par(1)
    assert partida.superficie_m2 == predio.superficie_m2
    assert partida.titular_ci == predio.propietario_ci
    assert partida.direccion == predio.direccion

    # 07: superficie distinta. 08: titular distinto. 09: CI distinto. 10: dirección distinta.
    assert par(7)[0].superficie_m2 != par(7)[1].superficie_m2
    assert par(8)[0].titular_nombre != par(8)[1].propietario_nombre
    assert par(9)[0].titular_ci != par(9)[1].propietario_ci
    assert par(10)[0].direccion != par(10)[1].direccion

    # 11: la partida cita un código que no existe en Catastro.
    assert por_matricula[seed_ddrr_catastro.matricula(11)].codigo_catastral not in por_codigo

    # 12: predio sin partida.
    assert seed_ddrr_catastro.matricula(12) not in por_matricula
    assert seed_ddrr_catastro.codigo(12) in por_codigo
