from typing import List
from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_mongo import PydanticObjectId
from typing import Optional
import re

class User(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    name: str
    email: str
    password: str
    role: str

    @field_validator('email')
    def validate_email(cls, v):
        email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(v):
            raise ValueError('Invalid email format')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

    @field_validator('email')
    def validate_email(cls, v):
        email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(v):
            raise ValueError('Invalid email format')
        return v

class UserNew(BaseModel):
    name: str
    email: str
    password: str
    role: str

    @field_validator('email')
    def validate_email(cls, v):
        email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(v):
            raise ValueError('Invalid email format')
        return v

class UserList(BaseModel):
    users: List[User]
