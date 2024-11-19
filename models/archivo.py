from typing import List

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Archivo(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    nombre: str
    url: str

class ArchivoNew(BaseModel):
    nombre: str
    url: str

class ArchivoUpdate(BaseModel):
    nombre: str
    url: str

class ArchivoList(BaseModel):
    archivos: List[Archivo]
