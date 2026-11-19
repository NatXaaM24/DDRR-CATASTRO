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
def borrar_documentos(limpieza, funcionario):
    """Borra los documentos de los usuarios de prueba antes de que la limpieza los borre."""
    yield
    with SessionLocal() as db:
        db.execute(delete(Documento).where(Documento.usuario_id.in_(limpieza)))
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


# --- Listar, ver detalle y servir el PDF (T-3.4) ---


def _ids(respuesta) -> set[str]:
    return {d["id"] for d in respuesta.json()["items"]}


def test_listar_funcionario_ve_solo_los_suyos(
    cliente, h_funcionario, h_otro_funcionario, borrar_documentos
):
    mio = _subir(cliente, h_funcionario, _pdf()).json()["id"]
    ajeno = _subir(cliente, h_otro_funcionario, _pdf()).json()["id"]

    r = cliente.get(URL, headers=h_funcionario)
    assert r.status_code == 200
    cuerpo = r.json()
    assert _ids(r) == {mio}
    assert cuerpo["total"] == 1
    assert ajeno not in _ids(r)
    assert "ruta" not in cuerpo["items"][0]


def test_listar_encargado_ve_todos(
    cliente, h_funcionario, h_encargado, h_otro_funcionario, borrar_documentos
):
    mio = _subir(cliente, h_funcionario, _pdf()).json()["id"]
    ajeno = _subir(cliente, h_otro_funcionario, _pdf()).json()["id"]

    r = cliente.get(URL, headers=h_encargado, params={"tamano": 100})
    assert r.status_code == 200
    assert {mio, ajeno} <= _ids(r)


def test_listar_filtros_y_paginacion(cliente, h_funcionario, borrar_documentos):
    _subir(cliente, h_funcionario, _pdf(), tipo="testimonio")
    plano = _subir(cliente, h_funcionario, _pdf(), tipo="plano_catastral").json()["id"]

    r = cliente.get(URL, headers=h_funcionario, params={"tipo": "plano_catastral"})
    assert _ids(r) == {plano}

    r = cliente.get(URL, headers=h_funcionario, params={"tamano": 1, "pagina": 2})
    cuerpo = r.json()
    assert cuerpo["total"] == 2
    assert len(cuerpo["items"]) == 1
    assert cuerpo["pagina"] == 2

    r = cliente.get(URL, headers=h_funcionario, params={"estado": "no_existe"})
    assert r.status_code == 422


def test_listar_sin_sesion(cliente):
    assert cliente.get(URL).status_code == 401


def test_detalle_propio_y_por_encargado(cliente, h_funcionario, h_encargado, borrar_documentos):
    documento_id = _subir(cliente, h_funcionario, _pdf()).json()["id"]
    for encabezados in (h_funcionario, h_encargado):
        r = cliente.get(f"{URL}/{documento_id}", headers=encabezados)
        assert r.status_code == 200
        assert r.json()["id"] == documento_id


def test_detalle_ajeno_responde_404(cliente, h_funcionario, h_otro_funcionario, borrar_documentos):
    documento_id = _subir(cliente, h_otro_funcionario, _pdf()).json()["id"]
    r = cliente.get(f"{URL}/{documento_id}", headers=h_funcionario)
    assert r.status_code == 404
    assert r.json()["code"] == "no_encontrado"


def test_detalle_inexistente_e_id_invalido(cliente, h_funcionario):
    assert cliente.get(f"{URL}/{uuid.uuid4()}", headers=h_funcionario).status_code == 404
    assert cliente.get(f"{URL}/no-es-uuid", headers=h_funcionario).status_code == 422


def test_servir_pdf(cliente, h_funcionario, h_encargado, funcionario, borrar_documentos):
    datos = _pdf()
    documento_id = _subir(cliente, h_funcionario, datos, nombre="testimonio ñ.pdf").json()["id"]

    for encabezados in (h_funcionario, h_encargado):
        r = cliente.get(f"{URL}/{documento_id}/pdf", headers=encabezados)
        assert r.status_code == 200
        assert r.content == datos
        assert r.headers["content-type"] == "application/pdf"
        assert r.headers["content-disposition"].startswith("inline")
        assert r.headers["cache-control"] == "no-store"

    with SessionLocal() as db:
        consulta = select(Bitacora).where(
            Bitacora.entidad_id == uuid.UUID(documento_id),
            Bitacora.accion == "documento_consultado",
        )
        assert len(list(db.scalars(consulta))) == 2


def test_servir_pdf_ajeno_responde_404(
    cliente, h_funcionario, h_otro_funcionario, borrar_documentos
):
    documento_id = _subir(cliente, h_otro_funcionario, _pdf()).json()["id"]
    r = cliente.get(f"{URL}/{documento_id}/pdf", headers=h_funcionario)
    assert r.status_code == 404


def test_servir_pdf_alterado_responde_409(
    cliente, h_funcionario, borrar_documentos, almacenamiento
):
    documento_id = _subir(cliente, h_funcionario, _pdf()).json()["id"]
    (pdf,) = almacenamiento.rglob("*.pdf")
    pdf.write_bytes(pdf.read_bytes() + b"%cambio")

    r = cliente.get(f"{URL}/{documento_id}/pdf", headers=h_funcionario)
    assert r.status_code == 409
    assert r.json()["code"] == "documento_alterado"
    with SessionLocal() as db:
        acciones = set(
            db.scalars(
                select(Bitacora.accion).where(Bitacora.entidad_id == uuid.UUID(documento_id))
            )
        )
    assert "documento_alterado" in acciones
    assert "documento_consultado" not in acciones


def test_servir_pdf_sin_sesion(cliente):
    assert cliente.get(f"{URL}/{uuid.uuid4()}/pdf").status_code == 401
