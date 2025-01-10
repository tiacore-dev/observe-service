from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

load_dotenv()

# Порт и биндинг
port = os.getenv('FLASK_PORT', '5000')
bind = f"0.0.0.0:{port}"

# Количество CPU
cpu_cores = cpu_count()


workers = max(2, min(4, cpu_cores // 2))  # Баланс между ядрами и воркерами
# worker_class = "gevent"  # Используем Gevent для асинхронности
threads = 4  # Увеличьте до 4 потоков на воркер


# Таймауты
timeout = 120  # Увеличьте таймаут для обработки длительных операций
keepalive = 5  # Увеличьте для соединений с повторным использованием


# Логи
loglevel = "info"
accesslog = "-"
errorlog = "-"

preload_app = True

worker_connections = 1000  # Максимум 1000 соединений для Gevent
max_requests = 500
max_requests_jitter = 50
