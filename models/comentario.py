from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Comentario(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaCreacion: datetime
    fechaEdicion: datetime

class ComentarioNew(BaseModel):
    idUsuario: PydanticObjectId
    idEntrada: PydanticObjectId
    contenido: str
    fechaCreacion: datetime = Field(default_factory=datetime.now)

class ComentarioUpdate(BaseModel):
    contenido: str
    fechaEdicion: datetime = Field(default_factory=datetime.now)

class ComentarioList(BaseModel):
    comentarios: List[Comentario]
