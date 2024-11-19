from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Wiki(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    nombre: str
