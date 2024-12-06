from app.database.models.chat import Chat
from app.database.db_globals import Session

class ChatManager:
    def __init__(self):
        self.Session = Session

    def add_chat(self, chat_id, chat_name=None):
        session = self.Session()
        try:
            chat = Chat(chat_id=chat_id, chat_name=chat_name)
            session.add(chat)
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
