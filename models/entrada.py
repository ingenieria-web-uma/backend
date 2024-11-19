from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List


class Entrada(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    idWiki: PydanticObjectId
    idVersionActual: PydanticObjectId
    nombre: str
    slug: str
    
class ColeccionEntradas(BaseModel):
    entradas: List[Entrada]