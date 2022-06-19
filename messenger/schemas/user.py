from datetime import datetime
from pydantic import BaseModel
from schemas.user_status import UserStatus


class UserModel(BaseModel):
    login: str
    password: str
    name: str


class User(UserModel):
    id: int
    status: UserStatus
    updated: datetime = None
    created: datetime
    chats: list

    class Config:
        orm_mode = True