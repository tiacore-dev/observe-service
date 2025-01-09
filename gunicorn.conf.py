from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

load_dotenv()

# Порт и биндинг
port = os.getenv('FLASK_PORT', '5000')
bind = f"0.0.0.0:{port}"


# Получение числа CPU
cpu_cores = cpu_count()


# Количество воркеров
workers = cpu_count() * 2 + 2  # Оставьте стандартное 2 CPU на воркер
worker_class = "gevent"

# Количество потоков на воркер
threads = 4  # Например, 4 потока на воркер

# Таймаут соединения
timeout = 120  # Уменьшите таймаут до 2 минут, чтобы не блокировать слишком долго
keepalive = 5  # Увеличьте keep-alive для повторных соединений

# Ограничение очереди соединений
worker_connections = 1000  # Для gevent, чтобы обработать больше соединений

# Логи
loglevel = "info"
accesslog = "-"
errorlog = "-"
