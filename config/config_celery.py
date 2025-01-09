import os
from dotenv import load_dotenv

load_dotenv()


class ConfigCelery:
    redis_port = os.getenv('REDIS_PORT')

    # Используем Redis для Celery
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

    # Основные настройки
    CELERY_TASK_TIME_LIMIT = 300
    CELERY_TASK_SOFT_TIME_LIMIT = 240
    CELERY_WORKER_CONCURRENCY = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = True
    CELERY_TASK_REJECT_ON_WORKER_LOST = True

    # Оптимизация соединений
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,
        'max_connections': 100
    }

    # Ретрай при ошибках
    CELERY_TASK_RETRY_DELAY = 10
    CELERY_TASK_MAX_RETRIES = 5

    # Логи
    CELERYD_LOG_LEVEL = 'INFO'
    CELERYD_HIJACK_ROOT_LOGGER = False

    # Отслеживание состояния задач
    CELERY_TRACK_STARTED = True
    CELERY_TASK_TRACK_STARTED = True
