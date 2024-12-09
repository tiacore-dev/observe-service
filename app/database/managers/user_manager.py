from sqlalchemy import exists
from app.database.models.user import User  
from app.database.db_globals import Session
import logging

class UserManager:
    def __init__(self):
        self.Session = Session

    def add_user(self, user_id, username=None):
        """Добавляем пользователя стандартно"""
        session = self.Session()
        new_user = User(user_id=user_id, username=username)
        session.add(new_user)
        session.commit()
        session.close()
        return user_id

    def user_exists(self, user_id):
        """Проверка существования пользователя по имени"""
        session = self.Session()
        exists_query = session.query(exists().where(User.user_id == user_id)).scalar()
        session.close()
        return exists_query
    
    def get_user_by_user_id(self, user_id):
        session = self.Session()
        try:
            # Получаем пользователя по id
            user = session.query(User).filter_by(user_id=user_id).first()
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

        # Возвращаем найденного пользователя или None, если не найдено
        return user

    def delete_user(self, user_id):
        """Удаление пользователя по user_id"""
        session = self.Session()
        try:
            # Ищем пользователя по user_id
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                # Если пользователь найден, удаляем его из сессии
                session.delete(user)
                session.commit()
                return True
            else:
                return False  # Если пользователь не найден, возвращаем False
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата
            session.close()

    def get_users(self):
        session = self.Session()
        try:
            # Ищем пользователя по user_id
            users = session.query(User).all()
            return users
        except Exception as e:
            logging.error(f"Ошибка при получении пользователей: {e}")
            raise e
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата
            session.close()

    def update_username(self, user_id, username):
        session = self.Session()
        try:
            user_in_db = session.query(User).filter_by(user_id=user_id).first()
            if user_in_db:
                user_in_db.username = username
                session.commit()
                logging.info(f"Обновлено имя пользователя {user_id}: {username}")
        except Exception as e:
            logging.error(f"Ошибка при редактировании имени пользователя: {e}")
            session.rollback()
            raise e
        finally:
            session.close()