import uuid
from sqlalchemy import exists
from app.database.models.admin import Admin
from app.database.db_globals import Session


class AdminManager:
    def __init__(self):
        self.Session = Session

    def add_admin(self, username, login, password):
        """Добавляем пользователя стандартно"""
        session = self.Session()
        user_id = str(uuid.uuid4())
        new_user = Admin(user_id=user_id, username=username, login=login)
        new_user.set_password(password)  # Устанавливаем хэш пароля
        session.add(new_user)
        session.commit()
        session.close()
        return user_id

    def check_password(self, username, password):
        """Проверяем пароль пользователя"""
        session = self.Session()
        user = session.query(Admin).filter_by(login=username).first()
        session.close()
        if user and user.check_password(password):
            return True
        return False

    def update_user_password(self, username, new_password):
        """Обновляем пароль пользователя"""
        session = self.Session()
        user = session.query(Admin).filter_by(login=username).first()
        if user:
            user.set_password(new_password)  # Обновляем хэш пароля
            session.commit()
        session.close()

    def user_exists(self, user_id):
        """Проверка существования пользователя по логину"""
        session = self.Session()
        try:
            # Используем exists с явной обработкой результата
            exists_query = session.query(
                exists().where(Admin.login == user_id)).scalar()
            return exists_query
        finally:
            session.close()

    def get_user_by_user_id(self, user_id):
        session = self.Session()
        try:
            # Получаем пользователя по id
            user = session.query(Admin).filter_by(user_id=user_id).first()
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

        # Возвращаем найденного пользователя или None, если не найдено
        return user

    def delete_user(self, login):
        """Удаление пользователя по user_id"""
        session = self.Session()
        try:
            # Ищем пользователя по user_id
            user = session.query(Admin).filter_by(login=login).first()
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
