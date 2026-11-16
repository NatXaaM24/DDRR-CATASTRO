import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BitacoraSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    usuario_id: uuid.UUID | None
    accion: str
    entidad: str
    entidad_id: uuid.UUID | None
    detalle: dict[str, Any] | None
