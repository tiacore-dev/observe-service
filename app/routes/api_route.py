from datetime import datetime
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


api_bp = Blueprint('api', __name__)


@api_bp.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    logging.info(f"""Запрос сообщений с фильтрацией: start_date={
                 start_date}, end_date={end_date}, user_id={user_id}, chat_id={chat_id}""")

    from app.database.managers.message_manager import MessageManager
    manager = MessageManager()

    try:
        # Преобразуем start_date и end_date, добавляя время, если нужно
        if start_date and isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)
        if end_date and isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        # Рассчитываем limit и offset
        offset = (page - 1) * page_size
        limit = page_size

        messages, total_count = manager.get_paginated_messages(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            chat_id=chat_id,
            limit=limit,
            offset=offset
        )

        logging.info(f"""Найдено {total_count} сообщений, возвращено {
                     len(messages)} сообщений на странице {page}""")
        return jsonify({
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'messages': [msg.to_dict() for msg in messages],
        }), 200
    except Exception as e:
        logging.error(f"Ошибка при фильтрации сообщений: {str(e)}")
        return jsonify({'error': 'Failed to fetch messages'}), 500

# Функция для безопасного парсинга даты


def parse_datetime(date_str, default_time):
    if not date_str:
        return None
    try:
        # Формат с временем
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=default_time[0], minute=default_time[1], second=default_time[2]
            )  # Если время отсутствует
        except ValueError as e:
            logging.error(
                f"Ошибка при разборе даты: {date_str} - {str(e)}")
            return None


@api_bp.route('/api/analyze', methods=['GET'])
@jwt_required()
def get_all_messages_for_analysis():
    """
    Возвращает все отфильтрованные сообщения для анализа.
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')

    logging.info(f"""Запрос всех сообщений для анализа: start_date={
                 start_date}, end_date={end_date}, user_id={user_id}, chat_id={chat_id}""")

    from app.database.managers.message_manager import MessageManager
    manager = MessageManager()

    # Корректируем start_date и end_date
    start_date = parse_datetime(start_date, (0, 0, 0))  # Начало дня
    end_date = parse_datetime(end_date, (23, 59, 59))  # Конец дня

    try:
        messages = manager.get_filtered_messages(
            start_date=start_date, end_date=end_date, user_id=user_id, chat_id=chat_id
        )
        logging.info(f"Найдено {len(messages)} сообщений для анализа.")
        return jsonify({'messages': [msg.to_dict() for msg in messages]}), 200
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений для анализа: {str(e)}")
        return jsonify({'error': 'Не удалось получить сообщения для анализа'}), 500


@api_bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Возвращает список пользователей из базы данных.
    """
    from app.database.managers.user_manager import UserManager
    user_manager = UserManager()
    try:
        users = user_manager.get_users()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {e}")
        return jsonify({"error": "Ошибка при получении списка пользователей"}), 500


@api_bp.route('/api/chats', methods=['GET'])
@jwt_required()
def get_chats():
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    current_user = get_jwt_identity()
    logging.info(f"Пользователь {current_user} запросил список чатов")
    try:
        chats = chat_manager.get_all_chats()
        logging.info(f"Найдено {len(chats)} чатов")
        return jsonify([chat.to_dict() for chat in chats]), 200
    except Exception as e:
        logging.error(f"Ошибка при получении списка чатов: {str(e)}")
        return jsonify({'error': 'Ошибка при получении чатов'}), 500


@api_bp.route('/api/prompts', methods=['GET'])
@jwt_required()
def get_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    logging.info(f"Пользователь {current_user} запросил список промптов")
    try:
        prompts = prompt_manager.get_all_prompts()
        logging.info(f"Найдено {len(prompts)} промптов")
        return jsonify([prompt.to_dict() for prompt in prompts]), 200
    except Exception as e:
        logging.error(f"Ошибка при получении списка промптов: {str(e)}")
        return jsonify({'error': 'Ошибка при получении промптов'}), 500


@api_bp.route('/api/download', methods=['GET'])
@jwt_required()
def download_file():
    s3_key = request.args.get('s3_key')
    if not s3_key:
        return jsonify({'error': 's3_key is required'}), 400

    from app.s3 import get_s3_manager, get_bucket_name
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    try:
        url = s3_manager.generate_presigned_url(
            bucket_name, f"telegram_docs/{s3_key}", expiration=3600)
        if url:
            return jsonify({'url': url}), 200
        else:
            return jsonify({'error': 'Failed to generate presigned URL'}), 500
    except Exception as e:
        logging.error(f"Ошибка при генерации URL для {s3_key}: {e}")
        return jsonify({'error': 'Internal server error'}), 500
