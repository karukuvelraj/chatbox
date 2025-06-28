from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.group_chat import Group, GroupMember, GroupMessage, GroupMessageSeen
from app.schemas.group_chat import GroupCreate, GroupMessageCreate, GroupMessageSeenStatus
from app.services.group_chat import create_group, create_group_message, mark_group_message_as_seen
from app.db.database import get_db


router = APIRouter()

@router.post("/groups/", response_model=Group)
def create_chat_group(group: GroupCreate, db: Session = Depends(get_db)):
    return create_group(db, group)


@router.post("/groups/{group_id}/messages/", response_model=GroupMessage)
def send_group_message(group_id: int, message: GroupMessageCreate, db: Session = Depends(get_db)):
    return create_group_message(db, message)


@router.get("/groups/{group_id}/messages/", response_model=List[GroupMessage])
def get_group_messages(group_id: int, db: Session = Depends(get_db)):
    return db.query(GroupMessage).filter(GroupMessage.group_id == group_id).all()


@router.put("/groups/{group_id}/messages/{message_id}/seen/", response_model=GroupMessageSeenStatus)
def mark_group_message_as_seen(group_id: int, message_id: int, seen_status: GroupMessageSeenStatus, db: Session = Depends(get_db)):
    return mark_group_message_as_seen(db, message_id, seen_status.user_id)


@router.get("/groups/{group_id}/messages/{message_id}/seen/", response_model=List[GroupMessageSeenStatus])
def get_seen_status_of_message(group_id: int, message_id: int, db: Session = Depends(get_db)):
    return db.query(GroupMessageSeen).filter(GroupMessageSeen.message_id == message_id).all()


@router.get("/groups/{group_id}/", response_model=Group)
def get_group_details(group_id: int, db: Session = Depends(get_db)):
    return db.query(Group).filter(Group.id == group_id).first()


@router.get("/users/{user_id}/groups/", response_model=List[Group])
def get_user_groups(user_id: int, db: Session = Depends(get_db)):
    return db.query(Group).join(GroupMember).filter(GroupMember.user_id == user_id).all()
