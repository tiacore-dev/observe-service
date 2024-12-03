from sqlalchemy import Column, String, BigInteger
from app.database.db_setup import Base 

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String) # Имя пользователя
    