import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import CredencialWebAuthn, IntentoLogin, RetoWebAuthn


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def guardar_reto(self, usuario_id: uuid.UUID, reto: bytes, expira_en: datetime) -> None:
        # Un solo reto por usuario: el nuevo reemplaza al anterior.
        self.db.execute(delete(RetoWebAuthn).where(RetoWebAuthn.usuario_id == usuario_id))
        self.db.add(RetoWebAuthn(usuario_id=usuario_id, reto=reto, expira_en=expira_en))
        self.db.flush()

    def consumir_reto(self, usuario_id: uuid.UUID) -> bytes | None:
        """Devuelve el reto vigente y lo borra (uso único)."""
        consulta = select(RetoWebAuthn).where(
            RetoWebAuthn.usuario_id == usuario_id,
            RetoWebAuthn.expira_en > datetime.now(UTC),
        )
        reto = self.db.scalars(consulta).first()
        valor = reto.reto if reto else None
        self.db.execute(delete(RetoWebAuthn).where(RetoWebAuthn.usuario_id == usuario_id))
        return valor

    def listar_credenciales(self, usuario_id: uuid.UUID) -> list[CredencialWebAuthn]:
        consulta = select(CredencialWebAuthn).where(CredencialWebAuthn.usuario_id == usuario_id)
        return list(self.db.scalars(consulta))

    def obtener_credencial(self, credential_id: bytes) -> CredencialWebAuthn | None:
        consulta = select(CredencialWebAuthn).where(
            CredencialWebAuthn.credential_id == credential_id
        )
        return self.db.scalars(consulta).first()

    def crear_credencial(self, credencial: CredencialWebAuthn) -> None:
        self.db.add(credencial)
        self.db.flush()

    # ---------- Intentos de login (R-SEG-6) ----------

    def registrar_fallo(self, username: str, ip: str) -> None:
        self.db.add(IntentoLogin(username=username, ip=ip))
        self.db.flush()

    def contar_fallos_usuario(self, username: str, desde: datetime) -> int:
        consulta = (
            select(func.count())
            .select_from(IntentoLogin)
            .where(IntentoLogin.username == username, IntentoLogin.created_at >= desde)
        )
        return self.db.scalar(consulta) or 0

    def contar_fallos_ip(self, ip: str, desde: datetime) -> int:
        consulta = (
            select(func.count())
            .select_from(IntentoLogin)
            .where(IntentoLogin.ip == ip, IntentoLogin.created_at >= desde)
        )
        return self.db.scalar(consulta) or 0

    def borrar_fallos_usuario(self, username: str) -> None:
        self.db.execute(delete(IntentoLogin).where(IntentoLogin.username == username))
