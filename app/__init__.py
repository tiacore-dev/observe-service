import logging
import os
from datetime import timedelta
import telebot
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from set_admin import set_admin
from app.database import init_db, set_db_globals
from app.s3 import init_s3_manager
from app.routes import register_routes
from app.openai_funcs import init_openai
from app.utils.tg_db import sync_chats_from_messages, update_usernames


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("app.log", mode="a"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # Используем 1 прокси для заголовка X-Forwarded-For
        x_proto=1,  # Учитываем X-Forwarded-Proto (HTTP/HTTPS)
        x_host=1,  # Учитываем X-Forwarded-Host
        x_port=1   # Учитываем X-Forwarded-Port
    )

    # Инициализация базы данных
    try:
        database_url = app.config['SQLALCHEMY_DATABASE_URI']
        engine, Session, Base = init_db(database_url)
        set_db_globals(engine, Session, Base)
        set_admin()
        logging.info("База данных успешно инициализирована.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")
        raise

    # Инициализация JWT
    try:
        JWTManager(app)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
        logging.info(f"""JWT инициализирован. {
            app.config['JWT_ACCESS_TOKEN_EXPIRES']}""")
    except Exception as e:
        logging.error(f"Ошибка при инициализации JWT: {e}")
        raise

    # Регистрация маршрутов
    try:
        register_routes(app)
        logging.info("Маршруты успешно зарегистрированы.")
    except Exception as e:
        logging.error(f"Ошибка при регистрации маршрутов: {e}")
        raise

    # Инициализация бота
    try:
        bot_token = os.getenv('TG_API_TOKEN')
        bot = telebot.TeleBot(bot_token)
        logging.info("Бот успешно инициализирован")
        sync_chats_from_messages(bot)
        update_usernames(bot)
        bot.stop_bot()
        logging.info("Бот успешно выполнил задачи и остановлен")
    except Exception as e:
        logging.error(f"Ошибка при инициализации бота: {e}")
        raise

    # Инициализация OpenAI
    try:
        init_openai(app)
        logging.info("OpenAI успешно инициализирован.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации OpenAI: {e}")
        raise

    # Инициализация S3
    try:
        init_s3_manager()
        logging.info("S3 менеджер успешно инициализирован.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации S3: {e}")
        raise

    return app
