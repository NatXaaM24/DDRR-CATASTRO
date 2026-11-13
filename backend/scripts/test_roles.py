from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.errors import registrar_manejadores
from app.modules.auth.dependencies import requiere_rol, usuario_actual
from app.modules.funcionarios.models import Rol, Usuario


def _cliente(rol: Rol | None) -> TestClient:
    app = FastAPI()
    registrar_manejadores(app)

    @app.get("/solo-encargado")
    def ruta(usuario: Annotated[Usuario, Depends(requiere_rol(Rol.encargado))]) -> dict[str, bool]:
        return {"ok": True}

    if rol is not None:
        usuario = Usuario(username="x", nombre_completo="x", password_hash="x", rol=rol)
        app.dependency_overrides[usuario_actual] = lambda: usuario
    return TestClient(app)


def test_encargado_puede_entrar() -> None:
    assert _cliente(Rol.encargado).get("/solo-encargado").status_code == 200


def test_funcionario_recibe_403() -> None:
    respuesta = _cliente(Rol.funcionario).get("/solo-encargado")
    assert respuesta.status_code == 403
    assert respuesta.json()["code"] == "sin_permiso"


def test_sin_sesion_recibe_401() -> None:
    assert _cliente(None).get("/solo-encargado").status_code == 401
