from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.chat_type import ChatType


class ChatModel(BaseModel):
    creator_user_id: int
    title: str
    description: Optional[str] = None
    chat_type: ChatType


class Chat(ChatModel):
    id: int
    created: datetime
    updated: datetime
    users: list

    class Config:
        orm_mode = True