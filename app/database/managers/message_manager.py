from app.database.models.messages import Message
from app.database.db_globals import Session
import logging
import uuid
from datetime import datetime, timedelta
from dateutil.parser import isoparse

class MessageManager:
    def __init__(self):
        self.Session = Session

    def add_message(self, timestamp, user_id, chat_id, text=None, s3_key=None):
        message_id = uuid.uuid4()
        #logging.info(f"Попытка записи сообщения {message_id} в базу данных.")
        session = self.Session()
        try:
            message_data = Message(
                message_id=message_id,
                timestamp=timestamp,
                user_id=user_id,
                chat_id=chat_id,
                text=text,
                s3_key=s3_key
            )
            # Сохранение данных в базу
            session.add(message_data)
            session.commit()
            #logging.info(f"Сообщение {message_id} успешно записано в базу данных.")
        except Exception as e:
            #logging.error(f"Ошибка записи сообщения {message_id} в базу данных: {e}")
            session.rollback()
        finally:
            session.close()

    def get_filtered_messages(self, start_date=None, end_date=None, user_id=None, chat_id=None):
        session = self.Session()
        query = session.query(Message)

        # Фильтр по периоду
        if start_date:
            if isinstance(start_date, str):
                try:
                    start_date_parsed = isoparse(start_date)  # Используем isoparse для строк с временными зонами
                except ValueError as e:
                    raise ValueError(f"Некорректный формат start_date: {start_date}") from e
            elif isinstance(start_date, datetime):
                start_date_parsed = start_date
            else:
                raise ValueError("start_date должен быть строкой в формате ISO 8601 или datetime.")
            query = query.filter(Message.timestamp >= start_date_parsed)

        if end_date:
            if isinstance(end_date, str):
                try:
                    end_date_parsed = isoparse(end_date)  # Используем isoparse для строк с временными зонами
                except ValueError as e:
                    raise ValueError(f"Некорректный формат end_date: {end_date}") from e
            elif isinstance(end_date, datetime):
                end_date_parsed = end_date
            else:
                raise ValueError("end_date должен быть строкой в формате ISO 8601 или datetime.")
            query = query.filter(Message.timestamp <= end_date_parsed)

        # Фильтр по пользователю
        if user_id:
            query = query.filter(Message.user_id == int(user_id))

        # Фильтр по чату
        if chat_id:
            query = query.filter(Message.chat_id == int(chat_id))

        return query.all()


    def get_paginated_messages(self, start_date=None, end_date=None, user_id=None, chat_id=None, limit=10, offset=0):
        session = self.Session()
        query = session.query(Message)

        # Фильтры
        if start_date:
            if isinstance(start_date, str):
                try:
                    start_date_parsed = isoparse(start_date)  # Поддержка ISO-строк
                except ValueError as e:
                    raise ValueError(f"Некорректный формат start_date: {start_date}") from e
            elif isinstance(start_date, datetime):
                start_date_parsed = start_date
            else:
                raise ValueError("start_date должен быть строкой в формате ISO 8601 или datetime.")
            query = query.filter(Message.timestamp >= start_date_parsed)

        if end_date:
            if isinstance(end_date, str):
                try:
                    end_date_parsed = isoparse(end_date)  # Поддержка ISO-строк
                except ValueError as e:
                    raise ValueError(f"Некорректный формат end_date: {end_date}") from e
            elif isinstance(end_date, datetime):
                end_date_parsed = end_date
            else:
                raise ValueError("end_date должен быть строкой в формате ISO 8601 или datetime.")
            query = query.filter(Message.timestamp <= end_date_parsed)

        if user_id:
            query = query.filter(Message.user_id == int(user_id))

        if chat_id:
            query = query.filter(Message.chat_id == int(chat_id))

        # Общее количество сообщений (для пагинации)
        total_count = query.count()

        # Применяем limit и offset
        query = query.order_by(Message.timestamp.desc()).limit(limit).offset(offset)

        return query.all(), total_count

