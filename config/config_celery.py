import os
from dotenv import load_dotenv

load_dotenv()


class ConfigCelery:
    redis_port = os.getenv('REDIS_PORT')
    # Используем Redis для Celery
    CELERY_BROKER_URL = f'redis://redis:{redis_port}/0'
    CELERY_RESULT_BACKEND = f'redis://redis:{redis_port}/0'
