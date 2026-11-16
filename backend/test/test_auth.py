import uuid
from datetime import timedelta

import pytest
from sqlalchemy import delete, func, select

from app.core import sesion
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.security import TIPO_ACCESO, TIPO_PREAUTH, TIPO_REFRESH, crear_token
from app.modules.auth.models import IntentoLogin
from app.modules.funcionarios.models import Usuario

CLAVE = "clave-de-prueba-123"  # la misma que usa conftest.py
MALA = "mala-clave-123"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"
REFRESH = "/api/v1/auth/refresh"
LOGOUT = "/api/v1/auth/logout"


@pytest.fixture(autouse=True)
def limpiar_intentos():
    """TestClient llega siempre con la IP 'testclient': se limpian sus fallos
    antes y después, para que una prueba no bloquee a la siguiente."""

    def borrar() -> None:
        with SessionLocal() as db:
            db.execute(delete(IntentoLogin).where(IntentoLogin.ip == "testclient"))
            db.commit()

    borrar()
    yield
    borrar()


def _login(cliente, username: str, password: str):
    return cliente.post(LOGIN, json={"username": username, "password": password})


def _contar_fallos(username: str) -> int:
    with SessionLocal() as db:
        consulta = (
            select(func.count()).select_from(IntentoLogin).where(IntentoLogin.username == username)
        )
        return db.scalar(consulta) or 0


def _token(usuario: Usuario, tipo: str, duracion: timedelta = timedelta(minutes=5)) -> str:
    return crear_token(str(usuario.id), tipo, duracion)


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _cookie(token: str) -> dict[str, str]:
    return {"Cookie": f"refresh_token={token}"}


# ---------- Login ----------


def test_login_correcto_devuelve_preauth_sin_sesion(cliente, funcionario):
    respuesta = _login(cliente, funcionario.username, CLAVE)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["preauth_token"]
    assert cuerpo["tiene_credencial"] is False
    assert "access_token" not in cuerpo  # la sesión real exige biometría (R-SEG-2)


def test_contrasena_incorrecta_da_401(cliente, funcionario):
    respuesta = _login(cliente, funcionario.username, MALA)
    assert respuesta.status_code == 401
    assert respuesta.json()["code"] == "no_autenticado"


def test_usuario_inexistente_da_el_mismo_error_que_uno_existente(cliente, funcionario):
    inexistente = _login(cliente, f"no_existe_{uuid.uuid4().hex[:6]}", CLAVE)
    existente = _login(cliente, funcionario.username, MALA)
    assert inexistente.status_code == existente.status_code == 401
    assert inexistente.json() == existente.json()  # no se puede adivinar quién existe


def test_usuario_desactivado_no_entra(cliente, funcionario):
    with SessionLocal() as db:
        db.get(Usuario, funcionario.id).activo = False
        db.commit()
    assert _login(cliente, funcionario.username, CLAVE).status_code == 401


# ---------- Límite de intentos ----------


def test_los_fallos_seguidos_bloquean_el_login(cliente, funcionario):
    maximo = get_settings().login_max_intentos_usuario
    for _ in range(maximo):
        assert _login(cliente, funcionario.username, MALA).status_code == 401

    bloqueado = _login(cliente, funcionario.username, MALA)
    assert bloqueado.status_code == 429
    assert bloqueado.json()["code"] == "demasiados_intentos"
    assert "retry-after" in bloqueado.headers
    # Mientras dura el bloqueo, ni la contraseña correcta entra.
    assert _login(cliente, funcionario.username, CLAVE).status_code == 429


def test_un_login_correcto_borra_los_fallos(cliente, funcionario):
    for _ in range(3):
        _login(cliente, funcionario.username, MALA)
    assert _contar_fallos(funcionario.username) == 3
    assert _login(cliente, funcionario.username, CLAVE).status_code == 200
    assert _contar_fallos(funcionario.username) == 0


# ---------- Tokens de acceso ----------


def test_me_con_sesion_activa(cliente, funcionario, h_funcionario):
    respuesta = cliente.get(ME, headers=h_funcionario)
    assert respuesta.status_code == 200
    assert respuesta.json()["username"] == funcionario.username


def test_me_sin_token_da_401(cliente):
    assert cliente.get(ME).status_code == 401


def test_token_vencido_da_401(cliente, funcionario):
    sesion.marcar_actividad(funcionario.id)
    vencido = _token(funcionario, TIPO_ACCESO, timedelta(seconds=-1))
    assert cliente.get(ME, headers=_bearer(vencido)).status_code == 401


def test_un_token_de_otro_tipo_no_sirve_como_acceso(cliente, funcionario):
    sesion.marcar_actividad(funcionario.id)
    for tipo in (TIPO_PREAUTH, TIPO_REFRESH):
        respuesta = cliente.get(ME, headers=_bearer(_token(funcionario, tipo)))
        assert respuesta.status_code == 401


# ---------- Inactividad (R-SEG-4) ----------


def test_sin_sesion_en_el_servidor_el_token_no_basta(cliente, funcionario):
    sesion.cerrar_sesion(funcionario.id)  # como si hubieran pasado 10 minutos sin actividad
    respuesta = cliente.get(ME, headers=_bearer(_token(funcionario, TIPO_ACCESO)))
    assert respuesta.status_code == 401
    assert respuesta.json()["code"] == "sesion_expirada"


# ---------- Refresh ----------


def test_refresh_renueva_los_tokens_y_entrega_la_cookie(cliente, funcionario):
    sesion.marcar_actividad(funcionario.id)
    respuesta = cliente.post(REFRESH, headers=_cookie(_token(funcionario, TIPO_REFRESH)))
    assert respuesta.status_code == 200
    assert respuesta.json()["access_token"]
    cookie = respuesta.headers["set-cookie"].lower()
    assert "refresh_token=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie


def test_refresh_con_la_sesion_cerrada_por_inactividad(cliente, funcionario):
    sesion.cerrar_sesion(funcionario.id)
    respuesta = cliente.post(REFRESH, headers=_cookie(_token(funcionario, TIPO_REFRESH)))
    assert respuesta.status_code == 401
    assert respuesta.json()["code"] == "sesion_expirada"


def test_refresh_sin_cookie_da_401(cliente):
    assert cliente.post(REFRESH).status_code == 401


# ---------- Logout ----------


def test_logout_cierra_la_sesion_en_el_servidor(cliente, funcionario, h_funcionario):
    assert cliente.get(ME, headers=h_funcionario).status_code == 200
    respuesta = cliente.post(LOGOUT, headers=_cookie(_token(funcionario, TIPO_REFRESH)))
    assert respuesta.status_code == 204
    # El token de acceso sigue sin vencer, pero ya no sirve.
    assert cliente.get(ME, headers=h_funcionario).status_code == 401


def test_logout_con_cookie_basura_no_falla(cliente):
    assert cliente.post(LOGOUT, headers=_cookie("basura")).status_code == 204
