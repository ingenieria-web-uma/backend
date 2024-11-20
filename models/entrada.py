from typing import List, Optional

from pydantic import BaseModel, Field, root_validator
from pydantic_mongo import PydanticObjectId


class Entrada(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str

class EntradaUpdate(BaseModel):
    idWiki: Optional[PydanticObjectId] = None
    idVersionActual: Optional[PydanticObjectId] = None
    nombre: Optional[str] = None
    slug: Optional[str] = None
    
    @root_validator(pre=True)
    def generar_slug(cls, valores):
        if "slug" in valores:
            valores["slug"] = None
        if "nombre" in valores:
            valores['slug'] = valores['nombre'].lower().replace(" ", "-")
        return valores

    class Config:
        exclude = {'slug'}

class EntradaNew(BaseModel):
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: Optional[str] = None

    @root_validator(pre=True)
    def generar_slug(cls, valores):
        if 'nombre' in valores:
            valores['slug'] = valores['nombre'].lower().replace(" ", "-")
        return valores

    class Config:
        exclude = {'slug'}

class EntradaList(BaseModel):
    entradas: List[Entrada]
