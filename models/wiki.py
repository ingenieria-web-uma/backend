from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_mongo import PydanticObjectId
from pymongo.common import validate

from models.baseMongo import MongoBase


class WikiFilter(BaseModel):
    nombre: Optional[Dict] = None

    @validator("nombre", always=True)
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v

class Wiki(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias='_id')
    nombre: str

class WikiUpdate(BaseModel, MongoBase):
    nombre: str

class WikiNew(BaseModel, MongoBase):
    nombre: str

class WikiList(BaseModel, MongoBase):
    wikis: List[Wiki]
