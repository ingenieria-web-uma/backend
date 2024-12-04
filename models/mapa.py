from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class MapaId(BaseModel, MongoBase):
    idMapa: PydanticObjectId


class Mapa(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    idEntrada: PydanticObjectId
    lat: float
    lon: float
    zoom: int


class MapaNew(BaseModel, MongoBase):
    idEntrada: PydanticObjectId
    lat: float
    lon: float
    zoom: int


class MapaUpdate(BaseModel, MongoBase):
    lat: Optional[float] = None
    lon: Optional[float] = None
    zoom: Optional[int] = None


class MapaList(BaseModel):
    mapas: List[Mapa]
