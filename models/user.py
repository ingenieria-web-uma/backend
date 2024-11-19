from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class User(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    name: str
    email: str
    password: str
    role: str

class UserUpdate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserNew(BaseModel):
    name: str
    email: str
    password: str
    role: str
