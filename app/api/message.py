from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.message import get_messages_between_users, get_user_messages
from app.schemas.message import MessageResponse
from app.db.database import get_db
from app.utils import auth


router = APIRouter()


@router.get("/", response_model=list[MessageResponse])
def read_messages(db: Session = Depends(get_db), user: User = Depends(auth.get_current_user)):
    messages = get_user_messages(db, user_id=user.id)
    if messages is None:
        return []
    return messages


@router.get("/{user1_id}/{user2_id}", response_model=dict)
def get_messages(user1_id: int, user2_id: int, limit: int = 50, offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    if current_user.id not in [user1_id, user2_id]:
        raise HTTPException(status_code=403, detail="Not authorized to view these messages")

    messages = get_messages_between_users(db=db, user1_id=user1_id, user2_id=user2_id, limit=limit, offset=offset)

    message_responses = [MessageResponse.from_orm(message) for message in messages]

    has_more = len(messages) == limit 

    return {
        "messages": message_responses,
        "has_more": has_more
    }


