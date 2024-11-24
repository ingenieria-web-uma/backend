from datetime import datetime
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    body: str

class EmailSchemaNew(BaseModel):
    email: EmailStr
    subject:str
    body:str