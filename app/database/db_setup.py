from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def init_db(database_url):

    engine = create_engine(database_url, echo=False)
    # Session = sessionmaker(bind=engine)
    Session = scoped_session(sessionmaker(bind=engine))
    # Создание всех таблиц
    # Base.metadata.create_all(engine)

    return engine, Session, Base
