from datetime import datetime
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field, validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class ComentarioFilter(BaseModel, MongoBase):
    idUsuario: Optional[PydanticObjectId] = Query(None)
    idEntrada: Optional[PydanticObjectId] = Query(None)
    contenido: Optional[str] = Query(None)
    editado: Optional[bool] = Query(None)

    @validator("contenido", always=True)
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v

class Comentario(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias='_id')
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaCreacion: datetime
    fechaEdicion: Optional[datetime] = None

class ComentarioNew(BaseModel, MongoBase):
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaCreacion: datetime = Field(default_factory=datetime.now)

class ComentarioUpdate(BaseModel, MongoBase):
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)

class ComentarioList(BaseModel, MongoBase):
    comentarios: List[Comentario]
