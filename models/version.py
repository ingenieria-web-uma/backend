from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from pydantic_mongo import PydanticObjectId


class Version(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)


class VersionUpdate(BaseModel):
    idUsuario: Optional[PydanticObjectId] = None
    idEntrada: Optional[PydanticObjectId] = None
    contenido: Optional[str] = None
    _fechaEdicion: datetime = PrivateAttr(default_factory=datetime.now)

    @property
    def fechaEdicion(self):
        return self._fechaEdicion


class VersionNew(BaseModel):
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    _fechaEdicion: datetime = PrivateAttr(default_factory=datetime.now)

    @property
    def fechaEdicion(self):
        return self._fechaEdicion


class VersionList(BaseModel):
    versiones: List[Version]
