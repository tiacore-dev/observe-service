from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

load_dotenv()

# Порт и биндинг
port = os.getenv('FLASK_PORT', '5000')
bind = f"0.0.0.0:{port}"


# Получение числа CPU
cpu_cores = cpu_count()

# Настройка воркеров
workers = cpu_cores * 2 + 3
worker_class = "gevent"

# Таймауты
timeout = 1200
keepalive = 1

# Логи
loglevel = "info"
errorlog = "-"
accesslog = "-"
capture_output = True
