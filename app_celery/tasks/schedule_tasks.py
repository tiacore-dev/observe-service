# from celery import app
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pytz import timezone
from celery import shared_task
from app.openai_funcs.openai_funcs import chatgpt_analyze
from app.utils.db_get import get_prompt


load_dotenv()

novosibirsk_tz = timezone('Asia/Novosibirsk')
now = datetime.now(novosibirsk_tz)


@shared_task
def analyze_task(chat_id, analysis_time):
    """
    Анализирует сообщения в чате за указанный временной промежуток.
    """
    logging.info(f"Начало анализа для чата {chat_id}")
    from app.database.managers.chat_manager import ChatManager
    from app.database.managers.message_manager import MessageManager
    chat_manager = ChatManager()
    message_manager = MessageManager()

    chat = chat_manager.get_chat_by_id(chat_id)
    if not chat:
        raise ValueError(f"Чат {chat_id} не найден.")

    now = datetime.now(novosibirsk_tz)

    analysis_start = datetime(
        year=now.year,
        month=now.month,
        day=now.day - 1,
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        tzinfo=novosibirsk_tz
    )

    analysis_end = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        tzinfo=novosibirsk_tz
    )

    logging.info(f"Диапазон анализа: {analysis_start} - {analysis_end}")

    messages = message_manager.get_filtered_messages(
        start_date=analysis_start.isoformat(),
        end_date=analysis_end.isoformat(),
        chat_id=chat_id
    )
    filters = {
        "chat_id": chat_id,
        "start_date": analysis_start.isoformat(),
        "end_date": analysis_end.isoformat(),
        "user_id": None
    }
    if not messages:
        raise ValueError(f"Нет сообщений для анализа в чате {chat_id}.")

    messages = [msg.to_dict() for msg in messages]
    prompt = get_prompt(
        chat.default_prompt_id) or "Системный промпт для анализа."

    analysis_result, tokens_input, tokens_output = chatgpt_analyze(
        prompt, messages
    )

    logging.info(f"Анализ завершён для чата {chat_id}.")
    return {
        "chat_id": chat_id,
        "analysis_result": analysis_result,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "prompt_id": chat.default_prompt_id,
        "filters": filters
    }


@shared_task
def save_analysis_result_task(data):
    """
    Сохраняет результат анализа в базу данных.
    """
    logging.info(f"Сохранение результата анализа для чата {data['chat_id']}.")
    from app.database.managers.analysis_manager import AnalysisManager
    analysis_manager = AnalysisManager()
    analysis_manager.save_analysis_result(
        data["prompt_id"],
        data["analysis_result"],
        data['filters'],
        data["tokens_input"],
        data["tokens_output"]
    )

    logging.info(f"Результат анализа сохранён для чата {data['chat_id']}.")


@shared_task
def send_analysis_result_task(data):
    """
    Отправляет результат анализа в Telegram.
    """
    from telebot import TeleBot
    bot_token = os.getenv('TG_API_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID')

    message_text = f"""Результат анализа для чата {
        data['chat_id']}:\n\n{data['analysis_result']}"""
    bot = TeleBot(bot_token)

    try:
        bot.send_message(chat_id=CHAT_ID, text=message_text)
        logging.info(f"Результат анализа отправлен в чат {data['chat_id']}.")
    except Exception as e:
        logging.error(f"Ошибка при отправке результата в Telegram: {e}")
    finally:
        bot.stop_bot()
