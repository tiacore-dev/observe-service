from sqlalchemy import Column, String, Text, DateTime, BigInteger
from datetime import datetime
from app.database.db_setup import Base 
import json


class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(String, primary_key=True)  # Уникальный идентификатор сообщения (64-битное число)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)  # Время отправки
    user_id = Column(BigInteger, nullable=False)  # Идентификатор пользователя (64-битное число)
    chat_id = Column(BigInteger, nullable=False)  # Идентификатор чата (64-битное число)
    text = Column(Text, nullable=True)  # Текст сообщения
    s3_key = Column(String, nullable=True)  # URL изображения (если есть)

    def __repr__(self):
        return f"<TelegramMessage(message_id={self.message_id}, user_id={self.user_id}, chat_id={self.chat_id}, text={self.text}, timestamp={self.timestamp})>"
    

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "text": self.text,
            "s3_key": self.s3_key
        }

    def to_json(self):
        return json.dumps(self.to_dict())