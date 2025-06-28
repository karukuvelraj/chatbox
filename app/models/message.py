from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import pytz


IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    sender_id = Column(Integer, ForeignKey('users.id'), index=True)
    receiver_id = Column(Integer, ForeignKey('users.id'), index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=get_ist_time, index=True)
    is_seen = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False) 
    
    sender = relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

    

