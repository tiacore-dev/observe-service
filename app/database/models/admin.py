from sqlalchemy import Column, String
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_setup import Base


class Admin(Base):
    __tablename__ = 'admins'

    user_id = Column(String, primary_key=True, autoincrement=False)
    username = Column(String)  # Имя пользователя
    login = Column(String, unique=True, nullable=False)  # Email или логин
    # Может быть NULL для OAuth-пользователей
    password_hash = Column(String, nullable=True)

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False
