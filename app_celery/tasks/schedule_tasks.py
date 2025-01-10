# from celery import app
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from pytz import timezone
from celery import shared_task


load_dotenv()

novosibirsk_tz = timezone('Asia/Novosibirsk')
now = datetime.now(novosibirsk_tz)

BOT_TOKEN = os.getenv('TG_API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


@shared_task(autoretry_for=(OperationalError,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def analyze_task(chat_id, analysis_time):
    """
    Анализирует сообщения в чате за указанный временной промежуток.
    """
    logging.info(f"Начало анализа для чата {chat_id}")
    from app.database.managers.chat_manager import ChatManager
    from app.database.managers.message_manager import MessageManager
    from app.utils.db_get import get_prompt
    from app.openai_funcs.openai_funcs import chatgpt_analyze
    chat_manager = ChatManager()
    message_manager = MessageManager()

    chat = chat_manager.get_chat_by_id(chat_id)
    if not chat:
        logging.error(f"Чат {chat_id} не найден.")
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
    ).astimezone(novosibirsk_tz)

    analysis_end = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        tzinfo=novosibirsk_tz
    ).astimezone(novosibirsk_tz)

    logging.info(f"Диапазон анализа: {analysis_start} - {analysis_end}")

    try:
        messages = message_manager.get_filtered_messages(
            start_date=analysis_start.isoformat(),
            end_date=analysis_end.isoformat(),
            chat_id=chat_id
        )
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений: {e}")
        raise

    filters = {
        "chat_id": chat_id,
        "start_date": analysis_start.isoformat(),
        "end_date": analysis_end.isoformat(),
        "user_id": None
    }

    if not messages:
        logging.warning(f"""Нет сообщений для анализа в чате {
                        chat_id} за период {analysis_start} - {analysis_end}.""")
        return {
            "chat_id": chat_id,
            "analysis_result": None,
            "tokens_input": 0,
            "tokens_output": 0,
            "prompt_id": chat['default_prompt_id'],
            "filters": filters
        }

    logging.info(f"Сообщений для анализа найдено: {len(messages)}")

    try:
        messages = [msg.to_dict() for msg in messages]
        prompt = get_prompt(chat['default_prompt_id'])
        if not prompt:
            raise ValueError(
                f"Промпт с ID {chat['default_prompt_id']} не найден.")

        analysis_result, tokens_input, tokens_output = chatgpt_analyze(
            prompt, messages)
    except Exception as e:
        logging.error(f"Ошибка при анализе сообщений: {e}")
        raise

    logging.info(f"Анализ завершён для чата {chat_id}.")
    return {
        "chat_id": chat_id,
        "analysis_result": analysis_result,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "prompt_id": chat['default_prompt_id'],
        "filters": filters
    }


@shared_task(autoretry_for=(OperationalError,), retry_backoff=5, retry_kwargs={'max_retries': 3})
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
    return data


@shared_task(autoretry_for=(OperationalError,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def send_analysis_result_task(data):
    """
    Отправляет результат анализа в Telegram.
    """
    if not data or not isinstance(data, dict):
        logging.error(
            "Переданы некорректные данные в send_analysis_result_task.")
        return
    from telebot import TeleBot

    message_text = f"""Результат анализа для чата {
        data['chat_id']}:\n\n{data['analysis_result']}"""
    bot = TeleBot(BOT_TOKEN)

    try:
        bot.send_message(chat_id=CHAT_ID, text=message_text)
        logging.info(f"Результат анализа отправлен в чат {data['chat_id']}.")
    except Exception as e:
        logging.error(f"Ошибка при отправке результата в Telegram: {e}")
    finally:
        bot.stop_bot()
