from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Wiki(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    nombre: str

class WikiUpdate(BaseModel):
    nombre: str

class WikiNew(BaseModel):
    nombre: str
