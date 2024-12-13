from app.database.models.chat import Chat
from app.database.db_globals import Session
from sqlalchemy import text
from datetime import datetime
import logging

class ChatManager:
    def __init__(self):
        self.Session = Session

    def add_chat(self, chat_id, chat_name=None):
        session = self.Session()
        try:
            # Выполнение SQL с поддержкой UPSERT
            session.execute(text("""
                INSERT INTO chats (chat_id, chat_name)
                VALUES (:chat_id, :chat_name)
                ON CONFLICT (chat_id) DO NOTHING;
            """), {"chat_id": chat_id, "chat_name": chat_name})
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def get_chat_by_id(self, chat_id):
        session = self.Session()
        try:
            return session.query(Chat).filter_by(chat_id=chat_id).first()
        finally:
            session.close()

    def update_chat_name(self, chat_id, new_name):
        session = self.Session()
        try:
            chat = session.query(Chat).filter_by(chat_id=chat_id).first()
            if chat:
                chat.chat_name = new_name
                session.commit()
            else:
                raise ValueError("Chat not found")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_chats(self):
        session = self.Session()
        try:
            return session.query(Chat).all()
        finally:
            session.close()


    def update_schedule(self, chat_id, schedule_analysis, prompt_id=None, analysis_time=None, send_time=None):
        """
        Обновить расписание для чата.
        """
        session = self.Session()
        try:
            chat = session.query(Chat).filter_by(chat_id=chat_id).first()
            if not chat:
                raise ValueError(f"Chat {chat_id} не найден")
            chat.schedule_analysis = schedule_analysis
            if prompt_id:
                chat.default_prompt_id = prompt_id
            if analysis_time:
                try:
                    # Пробуем распарсить как HH:MM, добавляем секунды, если их нет
                    chat.analysis_time = datetime.strptime(analysis_time, '%H:%M').time()
                except ValueError:
                    chat.analysis_time = datetime.strptime(analysis_time, '%H:%M:%S').time()

            if send_time:
                try:
                    # Пробуем распарсить как HH:MM, добавляем секунды, если их нет
                    chat.send_time = datetime.strptime(send_time, '%H:%M').time()
                except ValueError:
                    chat.send_time = datetime.strptime(send_time, '%H:%M:%S').time()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_chat(self, chat_id):
        session = self.Session()
        try:
            logging.info(f"Удаление чата '{chat_id}'")
            chat = session.query(Chat).filter_by(chat_id=chat_id).first()
            if chat:
                session.delete(chat)
                session.commit()
                logging.info(f"Чат '{chat_id}' успешно удален.")
            else:
                logging.warning(f"Чат '{chat_id}' не найден")
        except Exception as e:
            logging.error(f"Ошибка при удалении чата: {e}")
            session.rollback()
            raise e
        finally:
            session.close()
