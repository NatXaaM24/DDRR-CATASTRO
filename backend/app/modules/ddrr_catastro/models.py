"""Datos simulados de Derechos Reales (partidas) y Catastro (predios).

Son dos registros independientes, como en la realidad: la partida guarda el
código catastral como texto, sin clave foránea, para que se puedan detectar
discrepancias entre ambos (p. ej. un código que no existe en Catastro).
"""

from datetime import date
from decimal import Decimal

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import ModeloBase

# Coordenadas almacenadas en WGS 84 (R-BCK-7).
SRID_ALMACENAMIENTO = 4326
# Proyección métrica local para Cochabamba: WGS 84 / UTM zona 19S.
# Se usa para calcular áreas y distancias en metros con ST_Transform.
SRID_METRICO_LOCAL = 32719


class Partida(ModeloBase):
    """Inscripción de un inmueble en Derechos Reales (DDRR)."""

    __tablename__ = "partidas"

    # Matrícula computarizada del folio real, p. ej. "3.01.1.01.0001234".
    matricula: Mapped[str] = mapped_column(String(30), unique=True)
    titular_nombre: Mapped[str] = mapped_column(String(200))
    titular_ci: Mapped[str] = mapped_column(String(20))
    superficie_m2: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    direccion: Mapped[str] = mapped_column(String(300))
    codigo_catastral: Mapped[str] = mapped_column(String(30), index=True)
    fecha_inscripcion: Mapped[date] = mapped_column(Date)


class Predio(ModeloBase):
    """Inmueble registrado en Catastro, con su polígono."""

    __tablename__ = "predios"

    codigo_catastral: Mapped[str] = mapped_column(String(30), unique=True)
    propietario_nombre: Mapped[str] = mapped_column(String(200))
    propietario_ci: Mapped[str] = mapped_column(String(20))
    superficie_m2: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    direccion: Mapped[str] = mapped_column(String(300))
    distrito: Mapped[str] = mapped_column(String(50))
    geometria: Mapped[WKBElement] = mapped_column(
        Geometry("POLYGON", srid=SRID_ALMACENAMIENTO, spatial_index=True)
    )
