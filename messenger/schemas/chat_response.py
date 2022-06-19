from pydantic import BaseModel

from schemas.chat import Chat
from schemas.message import Message
from schemas.user import User


class ChatResponse(BaseModel):
    chat: Chat
    messages: list[Message]
    members: list[User]
