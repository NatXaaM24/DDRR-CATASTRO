import uuid

import pytest

from app.core.db import SessionLocal
from app.modules.bitacora.service import BitacoraService


def test_registrar_y_listar_por_accion():
    accion = f"prueba_{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        servicio = BitacoraService(db)
        servicio.registrar(accion, "prueba", detalle={"campo": "valor"})
        registros, total = servicio.listar(accion=accion)
        assert total == 1
        assert registros[0].detalle == {"campo": "valor"}
        db.rollback()  # no dejamos basura en la base


def test_paginacion():
    accion = f"prueba_{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        servicio = BitacoraService(db)
        for _ in range(3):
            servicio.registrar(accion, "prueba")
        pagina1, total = servicio.listar(accion=accion, pagina=1, tamano=2)
        pagina2, _ = servicio.listar(accion=accion, pagina=2, tamano=2)
        assert total == 3
        assert len(pagina1) == 2
        assert len(pagina2) == 1
        db.rollback()


def test_rechaza_datos_sensibles_en_el_detalle():
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            BitacoraService(db).registrar("x", "y", detalle={"password": "123"})
        db.rollback()
