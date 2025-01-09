import logging
import os
from dotenv import load_dotenv
import telebot

load_dotenv()

bot_token = os.getenv('TG_API_TOKEN')

CHAT_ID = os.getenv('CHAT_ID')


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
