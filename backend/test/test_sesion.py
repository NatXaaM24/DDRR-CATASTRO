import time
import uuid
from datetime import timedelta

from app.core import sesion
from app.core.db import SessionLocal
from app.core.security import TIPO_REFRESH, crear_token
from app.modules.auth.service import AuthService


def test_la_sesion_expira_por_inactividad(monkeypatch):
    monkeypatch.setattr(sesion, "_ttl", lambda: 1)  # 1 segundo en vez de 10 minutos
    usuario_id = uuid.uuid4()

    assert sesion.renovar_actividad(usuario_id) is False  # nunca inició sesión
    sesion.marcar_actividad(usuario_id)
    assert sesion.renovar_actividad(usuario_id) is True
    time.sleep(1.5)
    assert sesion.renovar_actividad(usuario_id) is False  # expiró


def test_cerrar_sesion_la_invalida():
    usuario_id = uuid.uuid4()
    sesion.marcar_actividad(usuario_id)
    sesion.cerrar_sesion(usuario_id)
    assert sesion.renovar_actividad(usuario_id) is False


def test_logout_cierra_la_sesion_en_redis():
    usuario_id = uuid.uuid4()
    sesion.marcar_actividad(usuario_id)
    token = crear_token(str(usuario_id), TIPO_REFRESH, timedelta(days=1))
    with SessionLocal() as db:
        AuthService(db).cerrar_sesion(token)
    assert sesion.renovar_actividad(usuario_id) is False


def test_logout_con_cookie_invalida_no_falla():
    with SessionLocal() as db:
        AuthService(db).cerrar_sesion("esto-no-es-un-token")
        AuthService(db).cerrar_sesion(None)
