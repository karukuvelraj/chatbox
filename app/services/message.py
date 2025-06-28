from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import User
from app.models.message import Message
from datetime import datetime


async def create_message(db: Session, sender_id: int, receiver_id: int, content: str, is_seen: bool = False, is_delivered: bool = False):
    db_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        is_seen=is_seen,
        is_delivered=is_delivered,
        timestamp=datetime.utcnow()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_user_messages(db: Session, user_id: int):
    subquery = db.query(Message.sender_id, Message.receiver_id, func.max(Message.timestamp).label("latest_timestamp")
    ).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).group_by(
        Message.sender_id, Message.receiver_id
    ).subquery()

    latest_messages = db.query(Message).join(
        subquery,
        (Message.sender_id == subquery.c.sender_id) &
        (Message.receiver_id == subquery.c.receiver_id) &
        (Message.timestamp == subquery.c.latest_timestamp)
    ).all()

    return latest_messages


def get_messages_between_users(db: Session, user1_id: int, user2_id: int, limit: int = 50, offset: int = 0):
    return db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
    
    
def update_is_delivered(db: Session, user_id: int):
    try:
        messages = db.query(Message).filter(Message.receiver_id == user_id, Message.is_delivered == False).all()
        if messages:
            for message in messages:
                message.is_delivered = True
            db.commit()
    
    except Exception as e:
        print(f"Error updating delivery status: {e}")

