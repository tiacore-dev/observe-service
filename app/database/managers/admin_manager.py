import uuid
from sqlalchemy import exists
from app.database.models.admin import Admin
from app.database.db_globals import Session


class AdminManager:
    def __init__(self):
        self.Session = Session

    def add_admin(self, username, login, password):
        """Добавляем пользователя стандартно"""
        user_id = str(uuid.uuid4())
        new_user = Admin(user_id=user_id, username=username, login=login)
        new_user.set_password(password)  # Устанавливаем хэш пароля

        with self.Session() as session:
            try:
                session.add(new_user)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
        return user_id

    def check_password(self, username, password):
        """Проверяем пароль пользователя"""
        with self.Session() as session:
            user = session.query(Admin).filter_by(login=username).first()
            if user and user.check_password(password):
                return True
        return False

    def update_user_password(self, username, new_password):
        """Обновляем пароль пользователя"""
        with self.Session() as session:
            user = session.query(Admin).filter_by(login=username).first()
            if user:
                try:
                    user.set_password(new_password)  # Обновляем хэш пароля
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e

    def user_exists(self, user_id):
        """Проверка существования пользователя по логину"""
        with self.Session() as session:
            return session.query(exists().where(Admin.login == user_id)).scalar()

    def get_user_by_user_id(self, user_id):
        """Получаем пользователя по user_id"""
        with self.Session() as session:
            return session.query(Admin).filter_by(user_id=user_id).first()

    def delete_user(self, login):
        """Удаление пользователя по user_id"""
        with self.Session() as session:
            user = session.query(Admin).filter_by(login=login).first()
            if user:
                try:
                    session.delete(user)
                    session.commit()
                    return True
                except Exception as e:
                    session.rollback()
                    raise e
            return False
