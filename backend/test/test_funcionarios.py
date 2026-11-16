import uuid

URL = "/api/v1/funcionarios"


def _datos(**extra):
    base = {
        "username": f"t_{uuid.uuid4().hex[:10]}",
        "nombre_completo": "Persona de Prueba",
        "password": "clave-de-prueba-123",
        "rol": "funcionario",
    }
    return base | extra


def _crear(cliente, headers, limpieza, **extra):
    respuesta = cliente.post(URL, json=_datos(**extra), headers=headers)
    assert respuesta.status_code == 201
    nuevo = respuesta.json()
    limpieza.append(uuid.UUID(nuevo["id"]))
    return nuevo


def test_el_encargado_crea_y_consulta(cliente, h_encargado, limpieza):
    nuevo = _crear(cliente, h_encargado, limpieza)
    assert nuevo["activo"] is True
    assert "password" not in nuevo and "password_hash" not in nuevo

    respuesta = cliente.get(f"{URL}/{nuevo['id']}", headers=h_encargado)
    assert respuesta.status_code == 200
    assert respuesta.json()["username"] == nuevo["username"]


def test_un_funcionario_no_puede_administrar(cliente, h_funcionario):
    assert cliente.get(URL, headers=h_funcionario).status_code == 403
    assert cliente.post(URL, json=_datos(), headers=h_funcionario).status_code == 403


def test_sin_token_es_401(cliente):
    assert cliente.get(URL).status_code == 401


def test_username_repetido_da_409(cliente, h_encargado, limpieza):
    nuevo = _crear(cliente, h_encargado, limpieza)
    repetido = cliente.post(URL, json=_datos(username=nuevo["username"]), headers=h_encargado)
    assert repetido.status_code == 409


def test_editar_cambia_solo_lo_enviado(cliente, h_encargado, limpieza):
    nuevo = _crear(cliente, h_encargado, limpieza)
    respuesta = cliente.patch(
        f"{URL}/{nuevo['id']}", json={"nombre_completo": "Nombre Nuevo"}, headers=h_encargado
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre_completo"] == "Nombre Nuevo"
    assert respuesta.json()["rol"] == "funcionario"


def test_eliminar_desactiva_sin_borrar(cliente, h_encargado, limpieza):
    nuevo = _crear(cliente, h_encargado, limpieza)
    assert cliente.delete(f"{URL}/{nuevo['id']}", headers=h_encargado).status_code == 204
    respuesta = cliente.get(f"{URL}/{nuevo['id']}", headers=h_encargado)
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False


def test_el_encargado_no_puede_desactivarse_a_si_mismo(cliente, encargado, h_encargado):
    respuesta = cliente.delete(f"{URL}/{encargado.id}", headers=h_encargado)
    assert respuesta.status_code == 422


def test_las_acciones_quedan_en_la_bitacora(cliente, encargado, h_encargado, limpieza):
    _crear(cliente, h_encargado, limpieza)
    respuesta = cliente.get(
        "/api/v1/bitacora",
        params={"usuario_id": str(encargado.id), "accion": "usuario_creado"},
        headers=h_encargado,
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["total"] >= 1


def test_el_listado_es_paginado(cliente, h_encargado):
    respuesta = cliente.get(URL, params={"tamano": 1}, headers=h_encargado)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["items"]) <= 1
    assert cuerpo["tamano"] == 1
    assert cuerpo["total"] >= 1
