import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import ModeloBase


class Bitacora(ModeloBase):
    """Una acción importante del sistema: quién, qué, sobre qué y cuándo."""

    __tablename__ = "bitacora"
    __table_args__ = (Index("ix_bitacora_created_at", "created_at"),)

    # Si algún día se borra el usuario, el registro se conserva con usuario_id vacío.
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    accion: Mapped[str] = mapped_column(String(60), index=True)
    entidad: Mapped[str] = mapped_column(String(60))
    entidad_id: Mapped[uuid.UUID | None] = mapped_column()
    detalle: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
