from typing import List, Optional

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
    nombre: Optional[str] = None
    url: Optional[str] = None

class ArchivoList(BaseModel):
    archivos: List[Archivo]
