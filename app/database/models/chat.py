from sqlalchemy import Column, String, BigInteger, Integer
from app.database.db_setup import Base
import json

class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(BigInteger, primary_key=True)  # Уникальный идентификатор чата
    chat_name = Column(String, nullable=True)  # Название чата
    default_prompt_id = Column(String, nullable=True)  # ID дефолтного промпта

    def __repr__(self):
        return f"<Chat(chat_id={self.chat_id}, chat_name={self.chat_name}, default_prompt_id={self.default_prompt_id})>"

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "chat_name": self.chat_name,
            "default_prompt_id": self.default_prompt_id
        }

    def to_json(self):
        return json.dumps(self.to_dict())
