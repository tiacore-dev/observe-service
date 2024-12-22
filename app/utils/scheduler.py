from datetime import datetime, timedelta
import logging
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import asyncio
from app.utils.db_get import get_prompt
from pytz import timezone
novosibirsk_tz = timezone('Asia/Novosibirsk')
now = datetime.now(novosibirsk_tz)

scheduler = BackgroundScheduler(
    jobstores={'default': MemoryJobStore()},
    timezone='Asia/Novosibirsk'
)

async def execute_analysis_and_send(chat_id, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат в Telegram.
    """
    logging.info(f'Начато выполнение задачи для чата: {chat_id}')
    from app.database.managers.message_manager import MessageManager
    from app.database.managers.chat_manager import ChatManager
    from app.openai_funcs.openai_funcs_async import chatgpt_analyze_async
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
            raise ValueError("analysis_start и analysis_end должны быть объектами datetime.")

        messages = message_manager.get_filtered_messages(
            start_date=analysis_start.isoformat(),  # Преобразуем datetime в строку ISO-формата
            end_date=analysis_end.isoformat(),      # Преобразуем datetime в строку ISO-формата
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
        prompt = get_prompt(chat.default_prompt_id) or "Системный промпт для анализа."
        analysis_result, tokens_input, tokens_output = await chatgpt_analyze_async(prompt, messages)
        analysis_id = analysis_manager.save_analysis_result(chat.default_prompt_id, analysis_result, filters, tokens_input, tokens_output)

        # Формирование текста результата
        result_text = f"Результат анализа:\n{analysis_result}\n\n"
        result_text += f"Токены ввода: {tokens_input}, Токены вывода: {tokens_output}"

        await send_analysis_result(analysis_result, chat.chat_name)

        logging.info(f"Анализ для чата {chat_id} успешно выполнен и отправлен.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении анализа для чата {chat_id}: {e}")





def start_scheduler():
    """
    Запуск планировщика с асинхронной обработкой и загрузкой задач из базы.
    """
    
    from app.database.managers.chat_manager import ChatManager
    # Инициализация задач из базы данных
    chat_manager = ChatManager()
    try:
        chats = chat_manager.get_all_chats()
        for chat in chats:
            if chat.schedule_analysis and chat.send_time:
                # Добавляем задачу для каждого чата с активным расписанием
                add_schedule_to_scheduler(
                    chat_id=chat.chat_id,
                    analysis_time=chat.analysis_time,
                    send_time=chat.send_time
                )
        logging.info("Все задачи из базы данных добавлены в планировщик.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации планировщика из базы данных: {e}")

    scheduler.start()
    logging.info("Планировщик успешно запущен.")



def add_schedule_to_scheduler(chat_id, analysis_time, send_time):
    """
    Добавляет или обновляет задачу анализа для указанного чата.
    """
    if not analysis_time or not send_time:
        logging.warning(f"Невозможно добавить задачу для чата {chat_id}: время анализа или отправки не указано.")
        return

    job_id = f"schedule_{chat_id}"

    # Удаляем существующую задачу, если она есть
    existing_job = scheduler.get_job(job_id=job_id)
    if existing_job:
        logging.info(f"Удаление существующей задачи для чата {chat_id} с ID {job_id}.")
        scheduler.remove_job(job_id=job_id)
    logging.info(f"Текущее время Новосибирска: {now}")
    # Добавляем новую задачу
    scheduler.add_job(
        run_async_analysis_and_send,
        'cron',
        hour=send_time.hour,
        minute=send_time.minute,
        args=[chat_id, analysis_time],
        id=job_id,
        replace_existing=True
    )
    logging.info(f"Задача для чата {chat_id} добавлена в планировщик: анализ в {analysis_time}, отправка в {send_time}.")
    list_scheduled_jobs()

def list_scheduled_jobs():
    for job in scheduler.get_jobs():
        logging.info(f"Job ID: {job.id}, trigger: {job.trigger}")

def run_async_analysis_and_send(chat_id, analysis_time):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(execute_analysis_and_send(chat_id, analysis_time))


def remove_schedule_from_scheduler(chat_id):
    job_id = f"schedule_{chat_id}"
    try:
        scheduler.remove_job(job_id)
        logging.info(f"Задача {job_id} успешно удалена из планировщика.")
    except JobLookupError:
        logging.warning(f"Задача {job_id} не найдена в планировщике.")


def clear_existing_jobs():
    """
    Удаляет все существующие задачи в планировщике.
    """
    try:
        scheduler.remove_all_jobs()
        logging.info("Все задачи успешно удалены из планировщика.")
    except Exception as e:
        logging.error(f"Ошибка при удалении всех задач: {e}")