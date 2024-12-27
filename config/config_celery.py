import os
from dotenv import load_dotenv

load_dotenv()


class ConfigCelery:
    redis_port = os.getenv('REDIS_PORT')
    # Используем Redis для Celery
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
