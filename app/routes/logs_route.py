from flask import Blueprint, request, jsonify
from flask import render_template
from flask_jwt_extended import jwt_required
import json
import os
from datetime import datetime

logs_bp = Blueprint('logs', __name__)
LOG_FILE_PATH = "app.log"  # Укажите путь к вашему лог-файлу


@logs_bp.route('/logs')  
def logs_page():
    return render_template('logs.html')




@logs_bp.route('/api/logs', methods=['GET'])
@jwt_required()
def get_logs():
    # Параметры фильтрации
    date = request.args.get('date')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))

    # Проверяем существование файла
    if not os.path.exists(LOG_FILE_PATH):
        return jsonify({'msg': 'Log file not found'}), 404

    logs = []
    total_count = 0

    # Читаем и фильтруем логи
    try:
        with open(LOG_FILE_PATH, "r") as log_file:
            for line in log_file:
                total_count += 1
                if offset <= total_count <= offset + limit:
                    log_entry = parse_log_entry(line, date)
                    if log_entry:
                        logs.append(log_entry)
    except Exception as e:
        return jsonify({'msg': f'Error reading log file: {str(e)}'}), 500

    return jsonify({'total': total_count, 'logs': logs})

from datetime import datetime

def parse_log_entry(line, date=None):
    """
    Парсинг строки лог-файла и фильтрация по дате.
    """
    try:
        # Пример строки: "2024-12-02 15:59:24,047 - INFO - Сообщение записано в базу."
        parts = line.split(" - ")
        log_date, log_level, message = parts[0], parts[1], parts[2]

        # Преобразуем дату логов в ISO-формат
        log_date_iso = datetime.strptime(log_date, "%Y-%m-%d %H:%M:%S,%f").isoformat()

        log_entry = {
            "date": log_date_iso,  # Дата в ISO-формате
            "level": log_level,
            "message": message.strip()
        }

        # Фильтрация по дате (только начало дня)
        if date:
            date_start = datetime.strptime(date, "%Y-%m-%d").date()
            log_date_parsed = datetime.fromisoformat(log_date_iso).date()
            if log_date_parsed != date_start:
                return None

        return log_entry
    except Exception:
        # Игнорируем строки, которые не соответствуют формату
        return None
