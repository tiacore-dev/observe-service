import os
from dotenv import load_dotenv
import multiprocessing

load_dotenv()

port = os.getenv('FLASK_PORT', '8000')  # Порт по умолчанию 8000

# Настройки Gunicorn
bind = f"0.0.0.0:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2  # Количество потоков на один воркер
timeout = 600
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 50
backlog = 2048

# Логи
loglevel = "info"
errorlog = "-"  # Логи ошибок выводятся в stderr
accesslog = "-"  # Логи доступа выводятся в stdout
capture_output = True  # Перехватывать вывод stdout/stderr из приложения

# Формат логов доступа
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
