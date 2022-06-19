from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.db.models import Message
from crud.crud_repository import Crud


class MessageRepository(Crud):
    def __init__(self):
        super().__init__(Message)

    def get_last_messages(self, chat_id: int, db: Session, offset: int = 0, limit: int = 20):
        messages = db.query(Message) .filter_by(chat_id=chat_id).order_by(desc(Message.created)).offset(offset).limit(limit).all()
        return messages