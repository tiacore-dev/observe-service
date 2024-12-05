from flask_jwt_extended import JWTManager
from flask import Flask
from app.database import init_db, set_db_globals
from app.s3 import init_s3_manager
from datetime import timedelta
import logging
import openai
from app.routes import register_routes
import os
from dotenv import load_dotenv
from app.openai_funcs import init_openai

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("app.log", mode="a"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)
# Настраиваем логирование
"""logging.basicConfig(
    level=logging.DEBUG,  # Устанавливаем уровень DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Логи будут выводиться в консоль
        logging.FileHandler('debug.log')  # Логи также сохраняются в файл debug.log
    ]
)"""

load_dotenv()

def create_app():
    app = Flask(__name__)
    # Установка секретного ключа для сессий
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    os.environ["http_proxy"] = ""
    os.environ["https_proxy"] = ""
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = "" 

    # Инициализация базы данных
    try:
        database_url = os.getenv('DATABASE_URL')
        engine, Session, Base = init_db(database_url)
        set_db_globals(engine, Session, Base)
        logging.info("База данных успешно инициализирована.", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация JWT
    try:
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
        jwt = JWTManager(app)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24) 
        logging.info(f"JWT инициализирован. {app.config['JWT_ACCESS_TOKEN_EXPIRES']}", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при инициализации JWT: {e}", extra={'user_id': 'init'})
        raise
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY') 
    # Инициализация OpenAI
    try:
        init_openai(app)
        logging.info("OpenAI успешно инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при инициализации OpenAI: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация S3
    try:
        init_s3_manager()
        logging.info("S3 менеджер успешно инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при инициализации S3: {e}", extra={'user_id': 'init'})
        raise

    # Регистрация маршрутов
    try:
        register_routes(app)
        logging.info("Маршруты успешно зарегистрированы.", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при регистрации маршрутов: {e}", extra={'user_id': 'init'})
        raise
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    return app
