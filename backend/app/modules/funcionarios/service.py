import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, ReglaDeNegocio
from app.core.security import hash_password
from app.modules.bitacora.service import BitacoraService
from app.modules.funcionarios.models import Rol, Usuario
from app.modules.funcionarios.repository import UsuarioRepository


class FuncionarioService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UsuarioRepository(db)
        self.bitacora = BitacoraService(db)

    def obtener_por_username(self, username: str) -> Usuario | None:
        return self.repo.obtener_por_username(username)

    def obtener_por_id(self, usuario_id: uuid.UUID) -> Usuario | None:
        return self.repo.obtener_por_id(usuario_id)

    def obtener(self, usuario_id: uuid.UUID) -> Usuario:
        usuario = self.repo.obtener_por_id(usuario_id)
        if usuario is None:
            raise NoEncontrado("Funcionario no encontrado.")
        return usuario

    def crear_usuario(
        self,
        username: str,
        nombre_completo: str,
        password: str,
        rol: Rol,
        *,
        actor_id: uuid.UUID | None = None,
    ) -> Usuario:
        if self.repo.obtener_por_username(username):
            raise Conflicto("El nombre de usuario ya existe.")
        usuario = Usuario(
            username=username,
            nombre_completo=nombre_completo,
            password_hash=hash_password(password),
            rol=rol,
        )
        self.repo.crear(usuario)
        self.bitacora.registrar(
            "usuario_creado",
            "usuario",
            usuario_id=actor_id,
            entidad_id=usuario.id,
            detalle={"rol": rol.value},
        )
        self.db.commit()
        return usuario

    def listar(
        self,
        *,
        rol: Rol | None = None,
        activo: bool | None = None,
        buscar: str | None = None,
        pagina: int = 1,
        tamano: int = 20,
    ) -> tuple[list[Usuario], int]:
        return self.repo.listar(
            rol=rol,
            activo=activo,
            buscar=buscar,
            limite=tamano,
            offset=(pagina - 1) * tamano,
        )

    def editar(
        self, usuario_id: uuid.UUID, cambios: dict[str, Any], *, actor_id: uuid.UUID
    ) -> Usuario:
        usuario = self.obtener(usuario_id)
        if usuario.id == actor_id and (
            ("rol" in cambios and cambios["rol"] != usuario.rol) or cambios.get("activo") is False
        ):
            raise ReglaDeNegocio("No puedes cambiar tu propio rol ni desactivar tu cuenta.")

        campos: list[str] = []
        if "nombre_completo" in cambios:
            usuario.nombre_completo = cambios["nombre_completo"]
            campos.append("nombre_completo")
        if "rol" in cambios:
            usuario.rol = cambios["rol"]
            campos.append("rol")
        if "activo" in cambios:
            usuario.activo = cambios["activo"]
            campos.append("activo")
        if "password" in cambios:
            usuario.password_hash = hash_password(cambios["password"])
            campos.append("credenciales")  # nunca se registra la contraseña (R-SEG-9)
        if not campos:
            raise ReglaDeNegocio("No se indicó ningún cambio.")

        self.bitacora.registrar(
            "usuario_editado",
            "usuario",
            usuario_id=actor_id,
            entidad_id=usuario.id,
            detalle={"campos": campos},
        )
        self.db.commit()
        return usuario

    def desactivar(self, usuario_id: uuid.UUID, *, actor_id: uuid.UUID) -> None:
        usuario = self.obtener(usuario_id)
        if usuario.id == actor_id:
            raise ReglaDeNegocio("No puedes desactivar tu propia cuenta.")
        if not usuario.activo:
            return  # ya estaba desactivado: repetir la acción no cambia nada
        usuario.activo = False
        self.bitacora.registrar(
            "usuario_desactivado", "usuario", usuario_id=actor_id, entidad_id=usuario.id
        )
        self.db.commit()
