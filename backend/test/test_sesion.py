import time
import uuid

from app.core import sesion


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
