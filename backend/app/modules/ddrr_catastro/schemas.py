import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class PartidaSalida(BaseModel):
    """Partida de Derechos Reales (DDRR)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    matricula: str
    titular_nombre: str
    titular_ci: str
    superficie_m2: Decimal
    direccion: str
    codigo_catastral: str
    fecha_inscripcion: date


class PredioSalida(BaseModel):
    """Predio de Catastro. La geometría va en GeoJSON, en SRID 4326."""

    id: uuid.UUID
    codigo_catastral: str
    propietario_nombre: str
    propietario_ci: str
    superficie_m2: Decimal
    direccion: str
    distrito: str
    geometria: dict[str, Any]
