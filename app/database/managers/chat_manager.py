from app.database.models.chat import Chat
from app.database.db_globals import Session
from sqlalchemy import text

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

    def update_default_prompt(self, chat_id, prompt_id):
        """Обновление дефолтного промпта для чата"""
        session = self.Session()
        try:
            chat = session.query(Chat).filter_by(chat_id=chat_id).first()
            if chat:
                chat.default_prompt_id = prompt_id
                session.commit()
            else:
                raise ValueError("Chat not found")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()