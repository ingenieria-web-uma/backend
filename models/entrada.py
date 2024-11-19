from typing import List

from pydantic import BaseModel, Field, root_validator
from pydantic_mongo import PydanticObjectId


class Entrada(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str = ""

    @root_validator(pre=True)
    def generar_slug(cls, valores):
        if 'slug' not in valores or not valores['slug']:
            valores['slug'] = valores['nombre'].lower().replace(" ", "-")
        return valores 

class EntradaUpdate(BaseModel):
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str = ""
    
    @root_validator(pre=True)
    def generar_slug(cls, valores):
        if 'slug' not in valores or not valores['slug']:
            valores['slug'] = valores['nombre'].lower().replace(" ", "-")
        return valores

class EntradaNew(BaseModel):
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str = ""

    @root_validator(pre=True)
    def generar_slug(cls, valores):
        if 'slug' not in valores or not valores['slug']:
            valores['slug'] = valores['nombre'].lower().replace(" ", "-")
        return valores

class EntradaList(BaseModel):
    entradas: List[Entrada]
