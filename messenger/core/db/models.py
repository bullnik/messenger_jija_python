from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from schemas.chat_type import ChatType
from schemas.user_status import UserStatus

Base = declarative_base()


chat_user = Table('chat_user', Base.metadata,
                  Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
                  Column('chat_id', Integer, ForeignKey('chats.id', ondelete="CASCADE"), nullable=False))


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    login = Column(String(256), unique=True, nullable=False)
    password = Column(String(256))
    status = Column(Enum(UserStatus), default=UserStatus.active)
    created = Column(DateTime(), server_default=func.now())
    updated = Column(DateTime(), server_default=func.now(), onupdate=func.now())
    chats = relationship('Chat', secondary=chat_user, back_populates='users')


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(String(512))
    chat_type = Column(Enum(ChatType), nullable=False)
    creator_user_id = Column(Integer, nullable=False)
    created = Column(DateTime(), server_default=func.now())
    updated = Column(DateTime(), server_default=func.now(), onupdate=func.now())
    users = relationship('User', secondary=chat_user, back_populates='chats')


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(1024), nullable=False)
    created = Column(DateTime(), server_default=func.now())
    updated = Column(DateTime(), server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete="CASCADE"))

