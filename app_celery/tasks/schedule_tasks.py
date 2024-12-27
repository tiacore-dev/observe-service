# from celery import app
import logging
from datetime import datetime
from pytz import timezone
from celery import shared_task  # pylint disable=import-error
from app.utils.db_get import get_prompt

novosibirsk_tz = timezone('Asia/Novosibirsk')
now = datetime.now(novosibirsk_tz)


@shared_task
def analyze_and_send_task(chat_id, analysis_time):
    logging.info(f'Начато выполнение задачи для чата: {chat_id}')
    from app.database.managers.message_manager import MessageManager
    from app.database.managers.chat_manager import ChatManager
    from app.openai_funcs.openai_funcs import chatgpt_analyze
    from app.utils.bot_utils import send_analysis_result
    from app.database.managers.analysis_manager import AnalysisManager

    chat_manager = ChatManager()
    message_manager = MessageManager()
    analysis_manager = AnalysisManager()

    try:
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat:
            logging.warning(f"Чат {chat_id} не найден.")
            return

        # Формируем диапазон времени для анализа
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

        # Убедимся, что анализируемый диапазон используется правильно
        if not isinstance(analysis_start, datetime) or not isinstance(analysis_end, datetime):
            raise ValueError(
                "analysis_start и analysis_end должны быть объектами datetime.")

        messages = message_manager.get_filtered_messages(
            # Преобразуем datetime в строку ISO-формата
            start_date=analysis_start.isoformat(),
            # Преобразуем datetime в строку ISO-формата
            end_date=analysis_end.isoformat(),
            chat_id=chat_id
        )
        messages = [msg.to_dict() for msg in messages]
        filters = {
            "chat_id": chat_id,
            "start_date": analysis_start.isoformat(),
            "end_date": analysis_end.isoformat(),
            "user_id": None
        }
        if not messages:
            logging.warning(f"Нет сообщений для анализа в чате {chat_id}.")
            return

        # Выполнение анализа
        prompt = get_prompt(
            chat.default_prompt_id) or "Системный промпт для анализа."
        analysis_result, tokens_input, tokens_output = chatgpt_analyze(
            prompt, messages)
        analysis_manager.save_analysis_result(
            chat.default_prompt_id, analysis_result, filters, tokens_input, tokens_output)

        # Формирование текста результата
        result_text = f"Результат анализа:\n{analysis_result}\n\n"
        result_text += f"""Токены ввода: {
            tokens_input}, Токены вывода: {tokens_output}"""

        send_analysis_result(analysis_result, chat.chat_name)

        logging.info(f"""Анализ для чата {
                     chat_id} успешно выполнен и отправлен.""")
    except Exception as e:
        logging.error(f"Ошибка при выполнении анализа для чата {chat_id}: {e}")
