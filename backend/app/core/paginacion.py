from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class Pagina[T](BaseModel):
    """Forma única de toda lista paginada (R-BCK-8)."""

    items: list[T]
    total: int
    pagina: int
    tamano: int


class Paginacion:
    def __init__(
        self,
        pagina: Annotated[int, Query(ge=1)] = 1,
        tamano: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> None:
        self.pagina = pagina
        self.tamano = tamano

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamano


ParametrosPagina = Annotated[Paginacion, Depends()]
