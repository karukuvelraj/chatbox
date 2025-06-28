from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.user import User


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship('User', secondary='group_members', back_populates='groups')
    messages = relationship('GroupMessage', back_populates='group')


class GroupMember(Base):
    __tablename__ = 'group_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    group = relationship('Group', back_populates='users')
    user = relationship('User', back_populates='groups')


class GroupMessage(Base):
    __tablename__ = 'group_messages'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_delivered = Column(Boolean, default=False)

    group = relationship('Group', back_populates='messages')
    sender = relationship('User', back_populates='sent_group_messages')
    seen_by = relationship('GroupMessageSeen', back_populates='message', cascade="all, delete-orphan")


class GroupMessageSeen(Base):
    __tablename__ = 'group_message_seen'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('group_messages.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_seen = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    message = relationship('GroupMessage', back_populates='seen_by')
    user = relationship('User', back_populates='group_message_seen')


