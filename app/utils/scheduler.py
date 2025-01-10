from datetime import datetime
import os
import logging
from pytz import timezone
from dotenv import load_dotenv
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from celery import chain
from app_celery.tasks import send_analysis_result_task, analyze_task, save_analysis_result_task

novosibirsk_tz = timezone('Asia/Novosibirsk')
now = datetime.now(novosibirsk_tz)

load_dotenv()

redis_port = os.getenv('REDIS_PORT')

scheduler = BackgroundScheduler(
    jobstores={
        'default': RedisJobStore(
            host='redis',  # Имя хоста Redis (или localhost)
            port=6379,     # Порт Redis
            db=0           # Номер базы Redis
        )
    },
    timezone='Asia/Novosibirsk'
)


def execute_analysis_and_send(chat_id, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат в Telegram.
    """
    task_chain = chain(
        analyze_task.s(chat_id, analysis_time),
        save_analysis_result_task.s(),
        send_analysis_result_task.s()
    )
    task_chain.apply_async()
    logging.info(f"Цепочка задач для чата {chat_id} запущена.")


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
        logging.error(
            f"Ошибка при инициализации планировщика из базы данных: {e}")

    scheduler.start()
    logging.info("Планировщик успешно запущен.")


def add_schedule_to_scheduler(chat_id, analysis_time, send_time):
    """
    Добавляет или обновляет задачу анализа для указанного чата.
    """
    if not analysis_time or not send_time:
        logging.warning(f"""Невозможно добавить задачу для чата {
                        chat_id}: время анализа или отправки не указано.""")
        return

    job_id = f"schedule_{chat_id}"

    # Удаляем существующую задачу, если она есть
    existing_job = scheduler.get_job(job_id=job_id)
    if existing_job:
        logging.info(f"""Удаление существующей задачи для чата {
                     chat_id} с ID {job_id}.""")
        scheduler.remove_job(job_id=job_id)
    logging.info(f"Текущее время Новосибирска: {now}")
    # Добавляем новую задачу
    scheduler.add_job(
        execute_analysis_and_send,
        'cron',
        hour=send_time.hour,
        minute=send_time.minute,
        args=[chat_id, analysis_time],
        id=job_id,
        replace_existing=True
    )
    logging.info(f"""Задача для чата {chat_id} добавлена в планировщик: анализ в {
                 analysis_time}, отправка в {send_time}.""")
    list_scheduled_jobs()


def list_scheduled_jobs():
    for job in scheduler.get_jobs():
        logging.info(f"Job ID: {job.id}, trigger: {job.trigger}")


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
