from sqlalchemy import Column, String, BigInteger
from app.database.db_setup import Base
import json

class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(BigInteger, primary_key=True)  # Уникальный идентификатор чата
    chat_name = Column(String, nullable=True)  # Название чата

    def __repr__(self):
        return f"<Chat(chat_id={self.chat_id}, chat_name={self.chat_name})>"

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "chat_name": self.chat_name
        }

    def to_json(self):
        return json.dumps(self.to_dict())
