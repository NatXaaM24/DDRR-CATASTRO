import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import DbSession
from app.core.paginacion import Pagina, ParametrosPagina
from app.modules.auth.dependencies import SoloEncargado
from app.modules.funcionarios.models import Rol
from app.modules.funcionarios.schemas import (
    FuncionarioCrear,
    FuncionarioEditar,
    FuncionarioSalida,
)
from app.modules.funcionarios.service import FuncionarioService

router = APIRouter(prefix="/funcionarios", tags=["Funcionarios"])


@router.post("", response_model=FuncionarioSalida, status_code=201)
def crear(datos: FuncionarioCrear, encargado: SoloEncargado, db: DbSession) -> FuncionarioSalida:
    usuario = FuncionarioService(db).crear_usuario(
        datos.username, datos.nombre_completo, datos.password, datos.rol, actor_id=encargado.id
    )
    return FuncionarioSalida.model_validate(usuario)


@router.get("", response_model=Pagina[FuncionarioSalida])
def listar(
    encargado: SoloEncargado,
    db: DbSession,
    paginacion: ParametrosPagina,
    rol: Rol | None = None,
    activo: bool | None = None,
    buscar: Annotated[str | None, Query(max_length=100)] = None,
) -> Pagina[FuncionarioSalida]:
    usuarios, total = FuncionarioService(db).listar(
        rol=rol,
        activo=activo,
        buscar=buscar,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
    return Pagina(
        items=[FuncionarioSalida.model_validate(u) for u in usuarios],
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.get("/{usuario_id}", response_model=FuncionarioSalida)
def ver(usuario_id: uuid.UUID, encargado: SoloEncargado, db: DbSession) -> FuncionarioSalida:
    return FuncionarioSalida.model_validate(FuncionarioService(db).obtener(usuario_id))


@router.patch("/{usuario_id}", response_model=FuncionarioSalida)
def editar(
    usuario_id: uuid.UUID,
    datos: FuncionarioEditar,
    encargado: SoloEncargado,
    db: DbSession,
) -> FuncionarioSalida:
    cambios = datos.model_dump(exclude_none=True)
    usuario = FuncionarioService(db).editar(usuario_id, cambios, actor_id=encargado.id)
    return FuncionarioSalida.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=204)
def desactivar(usuario_id: uuid.UUID, encargado: SoloEncargado, db: DbSession) -> None:
    FuncionarioService(db).desactivar(usuario_id, actor_id=encargado.id)
