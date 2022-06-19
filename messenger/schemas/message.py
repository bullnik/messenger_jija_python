from datetime import datetime

from pydantic import BaseModel


class MessageModel(BaseModel):
    user_id: int
    chat_id: int
    text: str


class Message(MessageModel):
    id: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True
