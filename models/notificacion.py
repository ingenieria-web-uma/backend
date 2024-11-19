import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

class Notification(BaseModel):
    id: Optional[PydanticObjectId]
    message: str = Field(..., min_length=1)
    is_read: bool = Field(default=False)
    timestamp: datetime 
    user_id: int 

class NotificationNew(BaseModel):
    message: str
    user_id: int

class NotificationUpdate(BaseModel):
    message: Optional[str] 
    is_read: Optional[bool]

class NotificationList(BaseModel):
    notifications: List[Notification]