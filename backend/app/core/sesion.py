import uuid
from functools import lru_cache

import redis

from app.core.config import get_settings
from app.core.errors import ServicioNoDisponible


@lru_cache
def _cliente() -> redis.Redis:
    return redis.Redis.from_url(
        get_settings().redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


def _ttl() -> int:
    return get_settings().inactivity_minutes * 60


def _clave(usuario_id: uuid.UUID) -> str:
    # El prefijo evita chocar con las claves que usa la cola de ARQ en el mismo Redis.
    return f"sesion:actividad:{usuario_id}"


def marcar_actividad(usuario_id: uuid.UUID) -> None:
    """Abre la sesión (o reinicia su cuenta regresiva)."""
    try:
        _cliente().set(_clave(usuario_id), "1", ex=_ttl())
    except redis.RedisError:
        raise ServicioNoDisponible() from None


def renovar_actividad(usuario_id: uuid.UUID) -> bool:
    """True si la sesión seguía activa (y la renueva). False si ya expiró."""
    try:
        return _cliente().getex(_clave(usuario_id), ex=_ttl()) is not None
    except redis.RedisError:
        raise ServicioNoDisponible() from None


def cerrar_sesion(usuario_id: uuid.UUID) -> None:
    try:
        _cliente().delete(_clave(usuario_id))
    except redis.RedisError:
        raise ServicioNoDisponible() from None
