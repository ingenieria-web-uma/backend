from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class WikiFilter(BaseModel):
    nombre: Annotated[Optional[Dict], Field(validate_default=True)] = None

    @field_validator("nombre")
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
