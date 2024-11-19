from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId


class User(BaseModel):
    id: PydanticObjectId
    name: str
