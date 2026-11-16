import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.modules.bitacora.models import Bitacora
from app.modules.bitacora.repository import BitacoraRepository

# R-SEG-9: nada de esto puede quedar escrito en la bitácora.
_CLAVES_PROHIBIDAS = ("password", "contrasena", "token", "secret", "hash", "cookie")


def _validar_detalle(detalle: dict[str, Any]) -> None:
    for clave in detalle:
        if any(prohibida in clave.lower() for prohibida in _CLAVES_PROHIBIDAS):
            raise ValueError(f"La clave '{clave}' no puede ir en la bitácora (R-SEG-9).")


class BitacoraService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BitacoraRepository(db)

    def registrar(
        self,
        accion: str,
        entidad: str,
        *,
        usuario_id: uuid.UUID | None = None,
        entidad_id: uuid.UUID | None = None,
        detalle: dict[str, Any] | None = None,
    ) -> None:
        """Agrega un registro. NO hace commit: lo confirma el servicio que la llama."""
        if detalle:
            _validar_detalle(detalle)
        self.repo.crear(
            Bitacora(
                usuario_id=usuario_id,
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                detalle=detalle,
            )
        )

    def listar(
        self,
        *,
        usuario_id: uuid.UUID | None = None,
        accion: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        pagina: int = 1,
        tamano: int = 20,
    ) -> tuple[list[Bitacora], int]:
        return self.repo.listar(
            usuario_id=usuario_id,
            accion=accion,
            desde=desde,
            hasta=hasta,
            limite=tamano,
            offset=(pagina - 1) * tamano,
        )
