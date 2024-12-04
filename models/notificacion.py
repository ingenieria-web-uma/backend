from datetime import datetime
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Notification(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    message: str = Field(..., min_length=1)
    is_read: bool = Field(default=False)
    timestamp: datetime
    user_id: PydanticObjectId
    entrada_id: PydanticObjectId


class NotificationNew(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: PydanticObjectId
    entrada_id: PydanticObjectId
    is_read: bool = Field(default=False)
    timestamp: datetime = Field(default=datetime.now())


class NotificationUpdate(BaseModel):
    message: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationList(BaseModel):
    notifications: List[Notification]
