import logging
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils import parse_time
from app.utils.tg_db import sync_chats_from_messages

chats_bp = Blueprint('chats', __name__)

# Настраиваем уровень логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@chats_bp.route('/manage_chats', methods=['GET'])
def manage_chats():
    logging.info("Страница управления чатами запрошена")
    return render_template('chats.html')


@chats_bp.route('/api/chats/<chat_id>/schedule', methods=['POST'])
@jwt_required()
def update_schedule(chat_id):
    """
    Обновить параметры расписания для конкретного чата.
    """
    data = request.json
    prompt_id = data.get('prompt_id')
    schedule_analysis = data.get('schedule_analysis')
    analysis_time = data.get('analysis_time')
    send_time = data.get('send_time')

    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()

    try:
        # Преобразуем строки времени в объекты time
        if analysis_time:
            analysis_time = parse_time(analysis_time)
        if send_time:
            send_time = parse_time(send_time)
        # Обновляем расписание в базе
        chat_manager.update_schedule(
            chat_id, schedule_analysis, prompt_id, analysis_time, send_time)

        logging.info(f"Расписание для чата {chat_id} успешно обновлено.")
        return jsonify({'message': 'Расписание успешно обновлено'}), 200
    except Exception as e:
        logging.error(
            f"Ошибка при обновлении расписания для чата {chat_id}: {e}")
        return jsonify({'error': 'Не удалось обновить расписание'}), 500


@chats_bp.route('/api/chats/update', methods=['POST'])
@jwt_required()
def update_chats():
    try:
        import os
        from dotenv import load_dotenv
        import telebot
        load_dotenv()
        bot_token = os.getenv('TG_API_TOKEN')
        bot = telebot.TeleBot(bot_token)
        sync_chats_from_messages(bot)
        # update_usernames(bot)
        bot.stop_bot()
        logging.info("Чаты успешно обновлены.")
        return {"msg": "Chats updated succsessfully"}, 200
    except Exception as e:
        logging.error(f"Возникла ошибка при обновлении чатов {e}.")
        return {"msg": f"Error during updating chats: {e}"}, 500
