from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

load_dotenv()

# Порт и биндинг
port = os.getenv('FLASK_PORT', '5000')
bind = f"0.0.0.0:{port}"

# Количество CPU
cpu_cores = cpu_count()


workers = 4  # Не более 4 воркеров, либо по количеству ядер
worker_class = "gevent"  # Используем Gevent для асинхронности
threads = 2  # Достаточно 2 потоков на воркер

# Таймауты
timeout = 60  # Более короткий таймаут
keepalive = 2  # Уменьшенное время жизни keep-alive

# Логи
loglevel = "info"
accesslog = "-"
errorlog = "-"

preload_app = True

worker_connections = 1000  # Максимум 1000 соединений для Gevent
max_requests = 1000  # Ограничьте число запросов на воркер перед перезапуском
max_requests_jitter = 50  # Добавьте небольшой рандом для распределения
