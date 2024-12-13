from datetime import datetime
import logging
from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('TG_API_TOKEN')
bot = Bot(bot_token)
chat_id = os.getenv('CHAT_ID')

def add_text(message, text, db_u, db):
    user_id = message.get('user_id')
    chat_id = message.get('chat_id')
    

    # Преобразуем timestamp из Unix в datetime
    timestamp = datetime.fromtimestamp(message.get('timestamp'))

    logging.info(f"Получено сообщение от пользователя {user_id} в чате {chat_id}.")

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
        logging.info(f"Сообщение от пользователя {user_id} успешно записано в базу.")
    except Exception as e:
        logging.error(f"Ошибка при записи сообщения от пользователя {user_id}: {e}")


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
        logging.info(f"Сообщение от пользователя {user_id} успешно записано в базу.")
    except Exception as e:
        logging.error(f"Ошибка при записи сообщения от пользователя {user_id}: {e}")


import requests

import requests
import logging

def send_analysis_with_chat_link(bot_token, target_chat_id, analysis_text, chat_username):
    """
    Отправляет текст анализа и ссылку на чат в Telegram.

    :param bot_token: Токен вашего Telegram-бота.
    :param target_chat_id: ID чата, куда нужно отправить сообщение.
    :param analysis_text: Текст анализа для отправки.
    :param chat_username: Username чата, на который нужно отправить ссылку.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Формируем сообщение
    message = (
        f"Результат анализа:\n{analysis_text}\n\n"
        f"Ссылка на чат: https://t.me/{chat_username}"
    )

    # Параметры запроса
    data = {
        "chat_id": target_chat_id,
        "text": message,
        "disable_web_page_preview": False  # Отображение превью, если есть описание чата
    }

    try:
        response = requests.post(url, data=data)

        if response.status_code == 200:
            logging.info(f"Сообщение успешно отправлено в чат {target_chat_id}.")
        else:
            logging.error(f"Ошибка отправки сообщения: {response.status_code}, {response.text}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в Telegram: {str(e)}")




def send_chat_link(bot_token, chat_id, target_chat_username):
    """
    Отправляет ссылку на другой чат в Telegram.

    :param bot_token: Токен вашего бота.
    :param chat_id: ID чата, куда нужно отправить ссылку.
    :param target_chat_username: Публичное имя (username) чата, на который вы хотите отправить ссылку.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = f"Ссылка на чат: https://t.me/{target_chat_username}"
    data = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        print("Ссылка успешно отправлена.")
    else:
        print(f"Ошибка отправки ссылки: {response.status_code}, {response.text}")


async def send_analysis_result(analysis_text, chat_name):
    message_text = f"Получен анализ текста для чата {chat_name}. Текст анализа: {analysis_text}"
    try:
        await bot.send_message(chat_id=chat_id, text=message_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")


