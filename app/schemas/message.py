from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    is_seen: Optional[bool] = False
    is_delivered: Optional[bool] = False

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        

        
        
