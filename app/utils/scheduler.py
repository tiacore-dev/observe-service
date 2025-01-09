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


def sync_schedules():
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()

    # Получение всех чатов с активным расписанием
    chats = chat_manager.get_all_chats()
    active_chat_ids = set(
        chat.chat_id for chat in chats if chat.schedule_analysis and chat.send_time)

    # Получение всех задач из планировщика
    existing_jobs = {job.id for job in scheduler.get_jobs()}

    # Добавляем новые задачи
    for chat in chats:
        if chat.chat_id not in existing_jobs and chat.schedule_analysis and chat.send_time:
            add_schedule_to_scheduler(
                chat.chat_id, chat.analysis_time, chat.send_time)

    # Удаляем неактуальные задачи
    for job_id in existing_jobs:
        if job_id.startswith("schedule_"):
            chat_id = job_id.replace("schedule_", "")
            if chat_id not in active_chat_ids:
                scheduler.remove_job(job_id)
                logging.info(f"Удалена неактуальная задача {job_id}.")


def start_scheduler():
    """
    Запуск планировщика с асинхронной обработкой и загрузкой задач из базы.
    """
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    try:
        chats = chat_manager.get_all_chats()
        for chat in chats:
            if chat.schedule_analysis and chat.send_time:
                add_schedule_to_scheduler(
                    chat_id=chat.chat_id,
                    analysis_time=chat.analysis_time,
                    send_time=chat.send_time
                )
        logging.info("Все задачи из базы данных добавлены в планировщик.")
    except Exception as e:
        logging.error(
            f"Ошибка при инициализации планировщика из базы данных: {e}")

    # Добавляем задачу синхронизации
    try:
        scheduler.add_job(
            sync_schedules,
            'interval',
            minutes=5,  # Интервал синхронизации
            id='sync_schedules',
            replace_existing=True
        )
    except Exception as e:
        logging.error(f"Ошибка при добавлении задачи синхронизации: {e}")

    scheduler.start()
    logging.info("Планировщик успешно запущен.")
    list_scheduled_jobs()


def add_schedule_to_scheduler(chat_id, analysis_time, send_time):
    job_id = f"schedule_{chat_id}"

    try:
        # Удаляем задачу, если она существует
        scheduler.remove_job(job_id=job_id)
        logging.info(f"Существующая задача {job_id} удалена.")
    except JobLookupError:
        logging.warning(f"Задача {job_id} не найдена для удаления.")

    # Добавляем новую задачу
    scheduler.add_job(
        func=execute_analysis_and_send,
        trigger='cron',
        id=job_id,
        hour=send_time.hour,
        minute=send_time.minute,
        args=[chat_id],
    )
    logging.info(f"""Задача {job_id} добавлена: анализ в {
                 analysis_time}, отправка в {send_time}.""")


def list_scheduled_jobs():
    for job in scheduler.get_jobs():
        logging.info(f"Job ID: {job.id}, trigger: {job.trigger}")


def remove_schedule_from_scheduler(job_id):
    try:
        scheduler.remove_job(job_id)
        logging.info(f"Задача {job_id} успешно удалена.")
    except JobLookupError:
        logging.warning(f"Задача {job_id} не найдена.")


def clear_existing_jobs():
    """
    Удаляет все существующие задачи в планировщике.
    """
    try:
        scheduler.remove_all_jobs()
        logging.info("Все задачи успешно удалены из планировщика.")
    except Exception as e:
        logging.error(f"Ошибка при удалении всех задач: {e}")
