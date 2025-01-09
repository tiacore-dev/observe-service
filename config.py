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
    CELERY_RESULT_BACKEND = os.getenv(
        'CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

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
