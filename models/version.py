from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class VersionId(BaseModel, MongoBase):
    idVersion: PydanticObjectId


class Version(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionNew(BaseModel, MongoBase):
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionUpdate(BaseModel, MongoBase):
    idUsuario: Optional[PydanticObjectId] = None
    idEntrada: Optional[PydanticObjectId] = None
    contenido: Optional[str] = None
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionList(BaseModel, MongoBase):
    versiones: List[Version]
