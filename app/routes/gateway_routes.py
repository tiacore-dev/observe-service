import logging
import json
import base64
from io import BytesIO
from flask import Blueprint, jsonify, request
from app.utils.bot_utils import add_text, add_file
from app.yandex_funcs.yandex_funcs import transcribe_audio

gateway_bp = Blueprint('gateway', __name__)


# Эндпоинт для получения данных от первого бота
@gateway_bp.route('/gateway/text', methods=['POST'])
def gateway():
    try:
        # Логируем сырые данные запроса
        logging.debug(f"""Получен запрос с данными: {
                      request.data.decode('utf-8')}""")

        # Парсим JSON
        data = request.get_json()
        if not data:
            logging.error("Не удалось распарсить JSON.")
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        message = data.get('message')
        if not message:
            logging.error("Отсутствует ключ 'message' в данных.")
            return jsonify({"status": "error", "message": "Missing 'message' key"}), 400

        # Логируем извлеченные данные
        logging.debug(f"Извлеченные данные сообщения: {message}")

        # Обработка сообщения
        if message.get('content_type') == 'text':
            handle_text(message)

        return jsonify({"status": "success", "message": "Message processed successfully"}), 200

    except Exception as e:
        # exc_info добавляет трейсбэк
        logging.error(f"Ошибка обработки запроса: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@gateway_bp.route('/gateway/file', methods=['POST'])
def upload_file():
    from app.s3 import get_s3_manager, get_bucket_name
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    try:
        # Логируем сырые данные запроса
        logging.debug(f"Получен запрос: {request.data.decode('utf-8')}")

        # Получаем JSON-данные из запроса
        data = request.get_json()
        if not data:
            logging.error("Не удалось распарсить JSON.")
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        # Логируем распарсенные данные
        logging.debug(f"Распарсенные данные: {json.dumps(data, indent=2)}")

        file_name = data.get('file_name')
        file_content = data.get('file_content')
        message = data.get('message')

        if not file_name or not file_content:
            logging.error(
                "Отсутствуют обязательные поля 'file_name' или 'file_content'.")
            return jsonify({"status": "error", "message": "Invalid file data"}), 400

        # Декодируем файл из Base64
        try:
            decoded_file = base64.b64decode(file_content)
            logging.debug(f"Файл {file_name} успешно декодирован.")
        except Exception as e:
            logging.error(f"Ошибка декодирования файла: {e}", exc_info=True)
            return jsonify({"status": "error", "message": f"File decode error: {e}"}), 500

        # Обрабатываем файл в зависимости от типа контента
        content_type = message.get('content_type')
        logging.debug(f"Тип контента: {content_type}")

        if content_type == 'photo':
            handle_photo(message, decoded_file, file_name,
                         s3_manager, bucket_name)
        elif content_type == 'document':
            handle_document(message, decoded_file, file_name,
                            s3_manager, bucket_name)
        elif content_type == 'voice':
            handle_voice(message, decoded_file)
        else:
            logging.error(f"Неподдерживаемый тип контента: {content_type}")
            return jsonify({"status": "error", "message": "Unsupported content type"}), 400

        logging.info(f"Файл {file_name} успешно обработан.")
        return jsonify({"status": "success", "message": f"File {file_name} uploaded successfully"}), 200

    except Exception as e:
        logging.error(f"Ошибка обработки запроса: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def handle_text(message):
    text = message.get('text')
    add_text(message, text)


def handle_photo(message, decoded_file, file_name, s3_manager, bucket_name):
    file_stream = BytesIO(decoded_file)
    s3_manager.upload_file(file_stream, bucket_name, file_name)
    add_file(message, file_name)


def handle_document(message, decoded_file, file_name, s3_manager, bucket_name):
    file_stream = BytesIO(decoded_file)
    s3_manager.upload_file(file_stream, bucket_name, file_name)
    add_file(message, file_name)


def handle_voice(message, decoded_file):
    # Дополнительно: транскрибируем аудио
    text = transcribe_audio(decoded_file, 'ogg')
    logging.info(text)
    add_text(message, text)
