from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class EntradaId(BaseModel, MongoBase):
    idEntrada: PydanticObjectId


class Entrada(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str
    idUsuario: PydanticObjectId
    nombreUsuario: str
    fechaCreacion: datetime


class EntradaUpdate(BaseModel, MongoBase):
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


class EntradaNew(BaseModel, MongoBase):
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: Optional[str] = None
    nombreUsuario: str
    idUsuario: PydanticObjectId
    fechaCreacion: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="before")
    def generar_slug(cls, valores):
        if "nombre" in valores:
            valores["slug"] = valores["nombre"].lower().replace(" ", "-")
        return valores

    class Config:
        exclude = {"slug"}


class EntradaList(BaseModel, MongoBase):
    entradas: List[Entrada]


class EntradaFiltro(BaseModel, MongoBase):
    idWiki: Optional[PydanticObjectId] = None
    idVersionActual: Optional[PydanticObjectId] = None
    nombre: Annotated[Optional[str], Field(validate_default=True)] = Query(None)
    idUsuario: Optional[PydanticObjectId] = None
    nombreUsuario: Annotated[Optional[str], Field(validate_default=True)] = Query(None)

    @field_validator("nombre")
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}
        return v
