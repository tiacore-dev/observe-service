from datetime import datetime
import logging
import os
from dotenv import load_dotenv
import telebot

load_dotenv()

bot_token = os.getenv('TG_API_TOKEN')

CHAT_ID = os.getenv('CHAT_ID')


def add_text(message, text, db_u, db):
    user_id = message.get('user_id')
    chat_id = message.get('chat_id')

    # Преобразуем timestamp из Unix в datetime
    timestamp = datetime.fromtimestamp(message.get('timestamp'))

    logging.info(f"""Получено сообщение от пользователя {
                 user_id} в чате {chat_id}.""")

    try:
        # Проверяем, есть ли пользователь в базе
        if not db_u.user_exists(user_id):
            db_u.add_user(user_id)

        # Добавляем сообщение в базу
        db.add_message(
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            text=text,
            s3_key=None
        )
        logging.info(f"""Сообщение от пользователя {
                     user_id} успешно записано в базу.""")
    except Exception as e:
        logging.error(
            f"Ошибка при записи сообщения от пользователя {user_id}: {e}")


def add_file(message, db_u, db, file_name):
    user_id = message.get('user_id')
    chat_id = message.get('chat_id')
    text = message.get('caption')
    # Преобразуем timestamp из Unix в datetime
    timestamp = datetime.fromtimestamp(message.get('timestamp'))
    try:
        # Проверяем, есть ли пользователь в базе
        if not db_u.user_exists(user_id):
            db_u.add_user(user_id)

        # Добавляем сообщение в базу
        db.add_message(
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            text=text,
            s3_key=file_name
        )
        logging.info(f"""Сообщение от пользователя {
                     user_id} успешно записано в базу.""")
    except Exception as e:
        logging.error(
            f"Ошибка при записи сообщения от пользователя {user_id}: {e}")


def send_analysis_result(analysis_text, chat_id):
    message_text = f"""Получен анализ текста для чата {
        chat_id}. Текст анализа: {analysis_text}"""
    bot = telebot.TeleBot(bot_token)
    try:

        # Отправляем сообщение
        bot.send_message(chat_id=CHAT_ID, text=message_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
    finally:
        # Завершаем работу бота и диспетчера
        bot.stop_bot()
