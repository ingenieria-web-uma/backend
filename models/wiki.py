from typing import Annotated, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class WikiFilter(BaseModel, MongoBase):
    nombre: Annotated[Optional[str], Field(validate_default=True)] = Query(None)

    @field_validator("nombre")
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v


class Wiki(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    nombre: str
    imagenUrl: str


class WikiUpdate(BaseModel, MongoBase):
    nombre: Optional[str] = None
    imagenUrl: Optional[str] = None


class WikiNew(BaseModel, MongoBase):
    nombre: str
    imagenUrl: str = ""


class WikiList(BaseModel, MongoBase):
    wikis: List[Wiki]
