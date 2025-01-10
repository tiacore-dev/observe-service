import os
from dotenv import load_dotenv

load_dotenv()


class ConfigFlask:

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ENDPOINT_URL = os.getenv('ENDPOINT_URL')
    REGION_NAME = os.getenv('REGION_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    CORS_ORIGINS = os.getenv('ORIGIN', '*')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(ConfigFlask):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ENV = 'development'


class ProductionConfig(ConfigFlask):
    DEBUG = False
    ENV = 'production'
    JWT_ACCESS_TOKEN_EXPIRES = 7200  # Продолжительность токена увеличена


class CeleryConfig(ConfigFlask):
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    result_backend = os.getenv(
        'CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    # Таймаут соединения с брокером (в секундах)
    broker_transport_options = {
        'visibility_timeout': 3600,  # Таймаут видимости задачи (1 час)
        'polling_interval': 2.0      # Интервал проверки новых задач
    }

    # Таймаут выполнения задачи
    # Мягкий лимит на выполнение задачи (в секундах)
    task_soft_time_limit = 300
    task_time_limit = 600       # Жесткий лимит на выполнение задачи

    # Максимальное количество попыток выполнения задачи
    task_max_retries = 5

    # Настройки пула воркеров
    worker_concurrency = 4  # Количество воркеров
    worker_prefetch_multiplier = 1  # Количество задач на одного воркера

    # Мониторинг и логи
    worker_hijack_root_logger = False  # Отключение перехвата логов
    task_track_started = True          # Отслеживание статуса "started"
    worker_log_format = (
        '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
    )
