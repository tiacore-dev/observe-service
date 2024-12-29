import multiprocessing
import os
from dotenv import load_dotenv

load_dotenv()

port = os.getenv('FLASK_PORT')

bind = f"0.0.0.0:{port}"

# Получаем количество доступных ядер CPU
cpu_count = multiprocessing.cpu_count()

workers = cpu_count * 2  # Количество воркеров: 2 воркера на ядро
threads = 2  # Количество потоков на воркер
worker_class = "eventlet"  # Используем eventlet для асинхронной обработки
worker_connections = 1000  # Максимум соединений на воркера
timeout = 120  # Таймаут запросов


# Логи
loglevel = "info"
errorlog = "-"  # Логи ошибок выводятся в stderr
accesslog = "-"  # Логи доступа выводятся в stdout
capture_output = True  # Перехватывать вывод stdout/stderr из приложения
