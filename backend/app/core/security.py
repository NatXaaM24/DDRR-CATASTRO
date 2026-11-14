from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.errors import NoAutenticado

_hasher = PasswordHash.recommended()

ALGORITMO = "HS256"
TIPO_ACCESO = "access"
TIPO_REFRESH = "refresh"
TIPO_PREAUTH = "preauth"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def crear_token(sub: str, tipo: str, duracion: timedelta) -> str:
    ahora = datetime.now(UTC)
    payload = {"sub": sub, "type": tipo, "iat": ahora, "exp": ahora + duracion}
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITMO)


def decodificar_token(token: str, tipo: str) -> str:
    """Valida firma, expiración y tipo. Devuelve el 'sub' (id del usuario)."""
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise NoAutenticado("Sesión expirada o inválida. Inicia sesión de nuevo.") from None
    if payload.get("type") != tipo or not payload.get("sub"):
        raise NoAutenticado("Sesión expirada o inválida. Inicia sesión de nuevo.")
    return str(payload["sub"])
