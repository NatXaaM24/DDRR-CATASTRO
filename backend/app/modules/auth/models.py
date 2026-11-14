import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import ModeloBase


class CredencialWebAuthn(ModeloBase):
    """Un dispositivo biométrico registrado por un usuario."""

    __tablename__ = "credenciales_webauthn"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    credential_id: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    public_key: Mapped[bytes] = mapped_column(LargeBinary)
    sign_count: Mapped[int] = mapped_column(default=0)
    nombre: Mapped[str] = mapped_column(String(100), default="Dispositivo")


class RetoWebAuthn(ModeloBase):
    """El reto pendiente de un usuario. Solo existe uno por usuario y se usa una vez."""

    __tablename__ = "retos_webauthn"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    reto: Mapped[bytes] = mapped_column(LargeBinary)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IntentoLogin(ModeloBase):
    """Un intento de login fallido. Se usa para limitar intentos (R-SEG-6)."""

    __tablename__ = "intentos_login"

    username: Mapped[str] = mapped_column(String(50), index=True)
    ip: Mapped[str] = mapped_column(String(45), index=True)  # 45 caracteres = IPv6
