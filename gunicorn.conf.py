from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

load_dotenv()

# Порт и биндинг
port = os.getenv('FLASK_PORT', '5000')
bind = f"0.0.0.0:{port}"

# Количество CPU
cpu_cores = cpu_count()

# Настройки воркеров
workers = max(cpu_cores, 2)  # Минимум 2 воркера, либо количество CPU
worker_class = "gevent"  # Используем Gevent для асинхронности

# Потоки (для блокирующих операций)
threads = 2  # Умеренное количество потоков на воркер

# Таймауты
timeout = 60  # Более короткий таймаут
keepalive = 2  # Уменьшенное время жизни keep-alive

# Логи
loglevel = "info"
accesslog = "-"
errorlog = "-"
