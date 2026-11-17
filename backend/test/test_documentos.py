import hashlib
import uuid
from pathlib import Path

import pymupdf
import pytest
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.errors import DocumentoAlterado, NoEncontrado
from app.modules.bitacora.models import Bitacora
from app.modules.documentos.models import Documento
from app.modules.documentos.repository import DocumentoRepository
from app.modules.documentos.service import DocumentoService

URL = "/api/v1/documentos"


def _pdf(texto: str | None = None) -> bytes:
    """PDF real de una página; el texto aleatorio hace que cada hash sea distinto."""
    with pymupdf.open() as pdf:
        pagina = pdf.new_page()
        pagina.insert_text((72, 72), texto or f"Documento de prueba {uuid.uuid4()}")
        return pdf.tobytes()


def _subir(cliente, encabezados, datos: bytes, nombre="testimonio.pdf", tipo="testimonio"):
    return cliente.post(
        URL,
        headers=encabezados,
        files={"archivo": (nombre, datos, "application/pdf")},
        data={"tipo": tipo},
    )


@pytest.fixture(autouse=True)
def almacenamiento(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Los PDFs de las pruebas van a una carpeta temporal, nunca a storage/."""
    monkeypatch.setattr(get_settings(), "storage_dir", tmp_path)
    return tmp_path


@pytest.fixture
def borrar_documentos(funcionario):
    """Borra los documentos del funcionario antes de que la limpieza borre al usuario."""
    yield
    with SessionLocal() as db:
        db.execute(delete(Documento).where(Documento.usuario_id == funcionario.id))
        db.commit()


def test_subir_pdf_valido(cliente, h_funcionario, funcionario, borrar_documentos, almacenamiento):
    datos = _pdf()
    r = _subir(cliente, h_funcionario, datos, nombre="C:\\carpeta\\mi testimonio.pdf")
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["hash_sha256"] == hashlib.sha256(datos).hexdigest()
    assert cuerpo["tamano_bytes"] == len(datos)
    assert cuerpo["estado"] == "subido"
    assert cuerpo["nombre_original"] == "mi testimonio.pdf"
    assert cuerpo["usuario_id"] == str(funcionario.id)
    assert "ruta" not in cuerpo

    with SessionLocal() as db:
        documento = db.get(Documento, uuid.UUID(cuerpo["id"]))
        assert documento is not None
        assert (almacenamiento / documento.ruta).read_bytes() == datos
        registro = db.scalars(select(Bitacora).where(Bitacora.entidad_id == documento.id)).one()
        assert registro.accion == "documento_subido"


def test_archivo_falso_con_extension_pdf(cliente, h_funcionario, almacenamiento):
    r = _subir(cliente, h_funcionario, b"MZ\x90\x00 esto es un ejecutable", nombre="falso.pdf")
    assert r.status_code == 415
    assert r.json()["code"] == "archivo_no_valido"
    assert not any(almacenamiento.rglob("*"))


def test_cabecera_pdf_pero_contenido_roto(cliente, h_funcionario):
    r = _subir(cliente, h_funcionario, b"%PDF-1.7\nbasura sin estructura")
    assert r.status_code == 415
    assert r.json()["code"] == "archivo_no_valido"


def test_archivo_vacio(cliente, h_funcionario):
    r = _subir(cliente, h_funcionario, b"")
    assert r.status_code == 415


def test_archivo_demasiado_grande(cliente, h_funcionario, monkeypatch, almacenamiento):
    monkeypatch.setattr(get_settings(), "max_upload_mb", 1)
    datos = b"%PDF-1.7\n" + b"0" * (1024 * 1024)
    r = _subir(cliente, h_funcionario, datos)
    assert r.status_code == 413
    assert r.json()["code"] == "archivo_demasiado_grande"
    assert not any(almacenamiento.rglob("*"))


def test_documento_duplicado(cliente, h_funcionario, borrar_documentos):
    datos = _pdf()
    assert _subir(cliente, h_funcionario, datos).status_code == 201
    r = _subir(cliente, h_funcionario, datos, nombre="otro-nombre.pdf")
    assert r.status_code == 409
    assert r.json() == {"code": "documento_duplicado", "message": "Este documento ya fue subido"}


def test_duplicado_por_restriccion_unique(
    cliente, h_funcionario, borrar_documentos, monkeypatch, almacenamiento
):
    """Si dos subidas iguales pasan la consulta previa a la vez, la BD lo bloquea."""
    datos = _pdf()
    assert _subir(cliente, h_funcionario, datos).status_code == 201
    monkeypatch.setattr(DocumentoRepository, "obtener_por_hash", lambda self, h: None)

    r = _subir(cliente, h_funcionario, datos)
    assert r.status_code == 409
    assert r.json()["code"] == "documento_duplicado"
    # Solo queda en disco el PDF de la primera subida.
    assert len(list(almacenamiento.rglob("*.pdf"))) == 1
    assert not any(almacenamiento.rglob("*.parcial"))


def test_tipo_invalido(cliente, h_funcionario):
    r = _subir(cliente, h_funcionario, _pdf(), tipo="no_existe")
    assert r.status_code == 422
    assert r.json()["code"] == "datos_invalidos"


def test_sin_sesion(cliente):
    r = _subir(cliente, {}, _pdf())
    assert r.status_code == 401


def test_encargado_no_puede_subir(cliente, h_encargado):
    r = _subir(cliente, h_encargado, _pdf())
    assert r.status_code == 403


# --- Verificación de integridad (T-3.3, R-SEG-8) ---


@pytest.fixture
def documento_subido(cliente, h_funcionario, borrar_documentos, almacenamiento):
    """Sube un PDF y devuelve (id, ruta absoluta en disco)."""
    r = _subir(cliente, h_funcionario, _pdf())
    assert r.status_code == 201
    documento_id = uuid.UUID(r.json()["id"])
    with SessionLocal() as db:
        ruta = db.get(Documento, documento_id).ruta
    return documento_id, almacenamiento / ruta


def _registros_alterado(documento_id: uuid.UUID) -> list[Bitacora]:
    with SessionLocal() as db:
        consulta = select(Bitacora).where(
            Bitacora.entidad_id == documento_id, Bitacora.accion == "documento_alterado"
        )
        return list(db.scalars(consulta))


def test_integridad_documento_intacto(documento_subido, funcionario):
    documento_id, _ = documento_subido
    with SessionLocal() as db:
        assert DocumentoService(db).verificar_integridad(documento_id, usuario_id=funcionario.id)
    assert _registros_alterado(documento_id) == []


def test_integridad_archivo_modificado(documento_subido, funcionario):
    documento_id, ruta = documento_subido
    ruta.write_bytes(ruta.read_bytes() + b"%cambio")
    with SessionLocal() as db:
        assert not DocumentoService(db).verificar_integridad(
            documento_id, usuario_id=funcionario.id
        )
    (registro,) = _registros_alterado(documento_id)
    assert registro.detalle == {"motivo": "hash_distinto"}


def test_integridad_archivo_borrado(documento_subido, funcionario):
    documento_id, ruta = documento_subido
    ruta.unlink()
    with SessionLocal() as db:
        assert not DocumentoService(db).verificar_integridad(
            documento_id, usuario_id=funcionario.id
        )
    (registro,) = _registros_alterado(documento_id)
    assert registro.detalle == {"motivo": "archivo_faltante"}


def test_integridad_hash_vacio_en_bd(documento_subido, funcionario):
    documento_id, _ = documento_subido
    with SessionLocal() as db:
        db.get(Documento, documento_id).hash_sha256 = ""
        db.commit()
    with SessionLocal() as db:
        assert not DocumentoService(db).verificar_integridad(
            documento_id, usuario_id=funcionario.id
        )
    (registro,) = _registros_alterado(documento_id)
    assert registro.detalle == {"motivo": "hash_faltante"}


def test_integridad_hash_nulo():
    """La columna es NOT NULL, pero si llegara un NULL se trata como alterado."""
    documento = Documento(hash_sha256=None, ruta="documentos/no-existe.pdf")
    assert DocumentoService._motivo_alteracion(documento) == "hash_faltante"


def test_integridad_documento_inexistente(funcionario):
    with SessionLocal() as db, pytest.raises(NoEncontrado):
        DocumentoService(db).verificar_integridad(uuid.uuid4(), usuario_id=funcionario.id)


def test_asegurar_integridad_lanza_documento_alterado(documento_subido, funcionario):
    documento_id, ruta = documento_subido
    with SessionLocal() as db:
        DocumentoService(db).asegurar_integridad(documento_id, usuario_id=funcionario.id)
    ruta.write_bytes(b"%PDF-1.7 otro contenido")
    with SessionLocal() as db, pytest.raises(DocumentoAlterado):
        DocumentoService(db).asegurar_integridad(documento_id, usuario_id=funcionario.id)
