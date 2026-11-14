import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session
from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.core.config import get_settings
from app.core.errors import Conflicto, NoAutenticado, SinPermiso
from app.modules.auth.models import CredencialWebAuthn
from app.modules.auth.repository import AuthRepository
from app.modules.funcionarios.models import Usuario

logger = logging.getLogger(__name__)


class WebAuthnService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AuthRepository(db)
        self.settings = get_settings()

    def tiene_credencial(self, usuario: Usuario) -> bool:
        return len(self.repo.listar_credenciales(usuario.id)) > 0

    # ---------- Ayudantes ----------

    def _guardar_reto(self, usuario: Usuario, reto: bytes) -> None:
        expira = datetime.now(UTC) + timedelta(minutes=self.settings.reto_minutes)
        self.repo.guardar_reto(usuario.id, reto, expira)
        self.db.commit()

    def _tomar_reto(self, usuario: Usuario) -> bytes:
        reto = self.repo.consumir_reto(usuario.id)
        self.db.commit()  # se confirma el borrado aunque la verificación falle después
        if reto is None:
            raise NoAutenticado("El desafío expiró. Vuelve a intentarlo.")
        return reto

    def _exigir_primer_registro(self, usuario: Usuario) -> None:
        if self.tiene_credencial(usuario):
            raise SinPermiso("Ya tienes un dispositivo registrado.")

    # ---------- Registro ----------

    def opciones_registro(self, usuario: Usuario) -> str:
        self._exigir_primer_registro(usuario)
        opciones = generate_registration_options(
            rp_id=self.settings.webauthn_rp_id,
            rp_name=self.settings.webauthn_rp_name,
            user_id=usuario.id.bytes,
            user_name=usuario.username,
            user_display_name=usuario.nombre_completo,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
                resident_key=ResidentKeyRequirement.DISCOURAGED,
            ),
        )
        self._guardar_reto(usuario, opciones.challenge)
        return options_to_json(opciones)

    def verificar_registro(self, usuario: Usuario, credencial: dict[str, Any], nombre: str) -> None:
        self._exigir_primer_registro(usuario)
        reto = self._tomar_reto(usuario)
        try:
            verificado = verify_registration_response(
                credential=json.dumps(credencial),
                expected_challenge=reto,
                expected_rp_id=self.settings.webauthn_rp_id,
                expected_origin=self.settings.frontend_origin,
                require_user_verification=True,
            )
        except Exception:  # la librería lanza varios tipos de error
            logger.warning("Registro WebAuthn rechazado")
            raise NoAutenticado("No se pudo verificar el dispositivo.") from None

        if self.repo.obtener_credencial(verificado.credential_id):
            raise Conflicto("Este dispositivo ya está registrado.")

        self.repo.crear_credencial(
            CredencialWebAuthn(
                usuario_id=usuario.id,
                credential_id=verificado.credential_id,
                public_key=verificado.credential_public_key,
                sign_count=verificado.sign_count,
                nombre=nombre,
            )
        )
        self.db.commit()

    # ---------- Autenticación ----------

    def opciones_autenticacion(self, usuario: Usuario) -> str:
        credenciales = self.repo.listar_credenciales(usuario.id)
        if not credenciales:
            raise SinPermiso("Primero debes registrar un dispositivo.")
        opciones = generate_authentication_options(
            rp_id=self.settings.webauthn_rp_id,
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=c.credential_id) for c in credenciales
            ],
            user_verification=UserVerificationRequirement.REQUIRED,
        )
        self._guardar_reto(usuario, opciones.challenge)
        return options_to_json(opciones)

    def verificar_autenticacion(self, usuario: Usuario, credencial: dict[str, Any]) -> None:
        reto = self._tomar_reto(usuario)
        try:
            credential_id = base64url_to_bytes(str(credencial["id"]))
        except KeyError, ValueError:
            raise NoAutenticado("No se pudo verificar el dispositivo.") from None

        guardada = self.repo.obtener_credencial(credential_id)
        if guardada is None or guardada.usuario_id != usuario.id:
            raise NoAutenticado("No se pudo verificar el dispositivo.")

        try:
            verificado = verify_authentication_response(
                credential=json.dumps(credencial),
                expected_challenge=reto,
                expected_rp_id=self.settings.webauthn_rp_id,
                expected_origin=self.settings.frontend_origin,
                credential_public_key=guardada.public_key,
                credential_current_sign_count=guardada.sign_count,
                require_user_verification=True,
            )
        except Exception:
            logger.warning("Autenticación WebAuthn rechazada")
            raise NoAutenticado("No se pudo verificar el dispositivo.") from None

        guardada.sign_count = verificado.new_sign_count
        self.db.commit()
