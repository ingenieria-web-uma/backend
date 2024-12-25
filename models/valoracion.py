from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class ValoracionId(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")


class Valoracion(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    idUsuarioRedactor: str
    idUsuarioValorado: str
    nota: int = Field(..., ge=0, le=5)


class ValoracionNew(BaseModel, MongoBase):
    idUsuarioRedactor: str
    idUsuarioValorado: str
    nota: int = Field(..., ge=0, le=5)


class ValoracionUpdate(BaseModel, MongoBase):
    nota: int = Field(..., ge=0, le=5)


class ValoracionList(BaseModel):
    valoraciones: List[Valoracion]


class ValoracionFiltro(BaseModel, MongoBase):
    idUsuarioRedactor: Optional[str] = None
    idUsuarioValorado: Optional[str] = None
    nota: Optional[int] = Field(None, ge=0, le=5)
