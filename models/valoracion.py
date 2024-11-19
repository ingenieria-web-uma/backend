from typing import List

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Valoracion(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idUsuarioRedactor: PydanticObjectId
    idUsuarioValorado: PydanticObjectId
    nota : int = Field(..., ge=0, le=5)

class ValoracionNew(BaseModel):
    idUsuarioRedactor: PydanticObjectId
    idUsuarioValorado: PydanticObjectId
    nota : int = Field(..., ge=0, le=5)

class ValoracionUpdate(BaseModel):
    nota : int = Field(..., ge=0, le=5)

class ValoracionList(BaseModel):
    valoraciones: List[Valoracion]
