from sqlalchemy.orm import Session
from app.models.group_chat import Group, GroupMember, GroupMessage, GroupMessageSeen, User
from app.schemas.group_chat import GroupCreate, GroupMessageCreate


def create_group(db: Session, group: GroupCreate):
    new_group = Group(name=group.name)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    for user_id in group.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            group_member = GroupMember(group_id=new_group.id, user_id=user.id)
            db.add(group_member)

    db.commit()
    db.refresh(new_group)
    return new_group


def create_group_message(db: Session, message: GroupMessageCreate):
    new_message = GroupMessage(
        group_id=message.group_id,
        sender_id=message.sender_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    group_members = db.query(GroupMember).filter(GroupMember.group_id == message.group_id).all()
    for member in group_members:
        group_message_seen = GroupMessageSeen(
            message_id=new_message.id,
            user_id=member.user_id,
            is_seen=False
        )
        db.add(group_message_seen)

    db.commit()
    return new_message


def mark_group_message_as_seen(db: Session, message_id: int, user_id: int):
    message_seen = db.query(GroupMessageSeen).filter(
        GroupMessageSeen.message_id == message_id,
        GroupMessageSeen.user_id == user_id
    ).first()

    if message_seen:
        message_seen.is_seen = True
    else:
        new_seen_entry = GroupMessageSeen(
            message_id=message_id,
            user_id=user_id,
            is_seen=True
        )
        db.add(new_seen_entry)

    all_seen = db.query(GroupMessageSeen).filter(
        GroupMessageSeen.message_id == message_id,
        GroupMessageSeen.is_seen == False
    ).count() == 0  

    if all_seen:
        message = db.query(GroupMessage).filter(GroupMessage.id == message_id).first()
        if message:
            message.is_delivered = True

    db.commit()
    return message_seen
