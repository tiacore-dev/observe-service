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
from werkzeug.middleware.proxy_fix import ProxyFix
from app.utils.chat_sync import sync_chats_from_messages
import telebot

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

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # Используем 1 прокси для заголовка X-Forwarded-For
        x_proto=1,  # Учитываем X-Forwarded-Proto (HTTP/HTTPS)
        x_host=1,  # Учитываем X-Forwarded-Host
        x_port=1   # Учитываем X-Forwarded-Port
    )
    # Инициализация базы данных
    try:
        database_url = os.getenv('DATABASE_URL')
        engine, Session, Base = init_db(database_url)
        set_db_globals(engine, Session, Base)
        logging.info("База данных успешно инициализирована.", extra={'user_id': 'init'})
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация бота
    bot_token = os.getenv('TG_API_TOKEN')
    bot = telebot.TeleBot(bot_token)
    sync_chats_from_messages(bot)

    # Инициализация JWT
    try:
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
        jwt = JWTManager(app)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) 
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
 
    return app
