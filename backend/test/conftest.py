import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, or_

from app.core import sesion
from app.core.db import SessionLocal
from app.core.security import TIPO_ACCESO, crear_token
from app.main import app
from app.modules.bitacora.models import Bitacora
from app.modules.funcionarios.models import Rol, Usuario
from app.modules.funcionarios.service import FuncionarioService

CLAVE_PRUEBA = "clave-de-prueba-123"


@pytest.fixture
def limpieza():
    """Lista de ids de usuarios creados por la prueba; al terminar se borran."""
    ids: list[uuid.UUID] = []
    yield ids
    with SessionLocal() as db:
        db.execute(
            delete(Bitacora).where(or_(Bitacora.usuario_id.in_(ids), Bitacora.entidad_id.in_(ids)))
        )
        db.execute(delete(Usuario).where(Usuario.id.in_(ids)))
        db.commit()
    for usuario_id in ids:
        sesion.cerrar_sesion(usuario_id)


def _nuevo_usuario(rol: Rol, limpieza: list[uuid.UUID]) -> Usuario:
    with SessionLocal() as db:
        usuario = FuncionarioService(db).crear_usuario(
            f"t_{uuid.uuid4().hex[:10]}", "Usuario de Prueba", CLAVE_PRUEBA, rol
        )
    limpieza.append(usuario.id)
    return usuario


def _encabezados(usuario: Usuario) -> dict[str, str]:
    token = crear_token(str(usuario.id), TIPO_ACCESO, timedelta(minutes=5))
    sesion.marcar_actividad(usuario.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)


@pytest.fixture
def encargado(limpieza) -> Usuario:
    return _nuevo_usuario(Rol.encargado, limpieza)


@pytest.fixture
def funcionario(limpieza) -> Usuario:
    return _nuevo_usuario(Rol.funcionario, limpieza)


@pytest.fixture
def h_encargado(encargado) -> dict[str, str]:
    return _encabezados(encargado)


@pytest.fixture
def h_funcionario(funcionario) -> dict[str, str]:
    return _encabezados(funcionario)
