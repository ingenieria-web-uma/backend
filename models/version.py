from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class VersionId(BaseModel, MongoBase):
    idVersion: PydanticObjectId


class Version(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    idUsuario: str
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionNew(BaseModel, MongoBase):
    idUsuario: str
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionUpdate(BaseModel, MongoBase):
    idUsuario: Optional[str] = None
    idEntrada: Optional[PydanticObjectId] = None
    contenido: Optional[str] = None
    fechaEdicion: datetime = Field(default_factory=datetime.now)

class VersionFilter(BaseModel, MongoBase):
    idUsuario: Optional[str] = None
    idEntrada: Optional[PydanticObjectId] = None
    contenido: Optional[str] = None
    fechaEdicion: Optional[datetime] = None


class VersionList(BaseModel, MongoBase):
    versiones: List[Version]
