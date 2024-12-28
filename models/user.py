import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_mongo import PydanticObjectId

from models.baseMongo import MongoBase


class UserRole(str, Enum):
    admin = "admin"
    lector = "lector"
    redactor = "redactor"
    editor = "editor"


class User(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    googleId: str
    name: str
    email: EmailStr
    profile_picture: str
    access_token: str
    expires_in: int
    role: UserRole
    wants_emails: bool

class UserUpdate(BaseModel, MongoBase):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    role: Optional[UserRole] = None
    wants_emails: Optional[bool] = None

class UserNew(BaseModel, MongoBase):
    googleId: str
    name: str
    email: EmailStr
    profile_picture: str
    access_token: str
    expires_in: int
    role: UserRole = Field(default=UserRole.lector)
    wants_emails: bool = Field(default=True)


class UserList(BaseModel):
    users: List[User]
