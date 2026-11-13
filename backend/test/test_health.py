import logging

from fastapi.testclient import TestClient

from app.core.logging import FiltroDatosSensibles
from app.main import app


def test_health_responde_200() -> None:
    with TestClient(app) as client:
        respuesta = client.get("/api/v1/health")
    assert respuesta.status_code == 200


def test_filtro_oculta_contrasenas() -> None:
    registro = logging.LogRecord(
        "prueba", logging.INFO, "", 0, "login password=secreto123", None, None
    )
    FiltroDatosSensibles().filter(registro)
    assert "secreto123" not in registro.getMessage()
    assert "[OCULTO]" in registro.getMessage()
