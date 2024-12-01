from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class EntradaId(BaseModel, MongoBase):
    idEntrada: PydanticObjectId


class Entrada(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str
    nombreUsuario: str
    idUsuario: PydanticObjectId
    fechaCreacion: datetime


class EntradaUpdate(BaseModel):
    idWiki: Optional[PydanticObjectId] = None
    idVersionActual: Optional[PydanticObjectId] = None
    nombre: Optional[str] = None
    slug: Optional[str] = None
    nombreUsuario: Optional[str] = None
    idUsuario: Optional[PydanticObjectId] = None

    @model_validator(mode="before")
    def generar_slug(cls, valores):
        if "slug" in valores:
            valores["slug"] = None
        if "nombre" in valores:
            valores["slug"] = valores["nombre"].lower().replace(" ", "-")
        return valores

    class Config:
        exclude = {"slug"}


class EntradaNew(BaseModel):
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: Optional[str] = None
    nombreUsuario: str
    idUsuario: PydanticObjectId
    fechaCreacion: datetime = datetime.now()

    @model_validator(mode="before")
    def generar_slug(cls, valores):
        if "nombre" in valores:
            valores["slug"] = valores["nombre"].lower().replace(" ", "-")
        return valores

    class Config:
        exclude = {"slug"}


class EntradaList(BaseModel):
    entradas: List[Entrada]
