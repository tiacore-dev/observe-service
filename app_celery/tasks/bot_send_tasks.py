import logging
import os
from dotenv import load_dotenv
import telebot
from celery import shared_task

load_dotenv()

bot_token = os.getenv('TG_API_TOKEN')

CHAT_ID = os.getenv('CHAT_ID')


"""@shared_task
def send_analysis_result_task(analysis_text, chat_id):
    message_text = fПолучен анализ текста для чата {
    chat_id}. Текст анализа: {analysis_text}
    bot = telebot.TeleBot(bot_token)
    try:

        # Отправляем сообщение
        bot.send_message(chat_id=CHAT_ID, text=message_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
    finally:
        # Завершаем работу бота и диспетчера
        bot.stop_bot()"""
