from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GroupMessageBase(BaseModel):
    sender_id: int
    content: str


class GroupMessageCreate(GroupMessageBase):
    group_id: int


class GroupMessage(GroupMessageBase):
    id: int
    timestamp: datetime
    is_delivered: bool

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    user_ids: List[int]  


class Group(BaseModel):
    id: int
    name: str
    users: List[int]  

    class Config:
        from_attributes = True


class GroupMessageSeenStatus(BaseModel):
    message_id: int
    user_id: int
    is_seen: bool
    timestamp: datetime

    class Config:
        from_attributes = True
