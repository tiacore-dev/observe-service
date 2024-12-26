import logging
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required

from app.utils.tg_db import update_usernames

users_bp = Blueprint('users', __name__)


@users_bp.route('/manage_users', methods=['GET'])
def manage_users():
    logging.info("Страница управления чатами запрошена")
    return render_template('users.html')


@users_bp.route('/users/<user_id>/edit', methods=['POST'])
@jwt_required()
def update_user(user_id):
    """
    Обновить параметры расписания для конкретного чата.
    """
    data = request.json
    username = data.get('username')

    from app.database.managers.user_manager import UserManager
    db = UserManager()

    try:
        db.update_username(user_id, username)
        logging.info(f"Имя для пользователя {user_id} успешно обновлено.")
        return jsonify({'message': 'Имя пользователя успешно обновлено'}), 200
    except Exception as e:
        logging.error(
            f"Ошибка при обновлении имени для пользователя {user_id}: {e}")
        return jsonify({'error': 'Не удалось обновить имя пользователя'}), 500


@users_bp.route('/api/users/update', methods=['POST'])
@jwt_required()
def update_users():
    try:
        import os
        from dotenv import load_dotenv
        import telebot
        load_dotenv()
        bot_token = os.getenv('TG_API_TOKEN')
        bot = telebot.TeleBot(bot_token)
        update_usernames(bot)
        bot.stop_bot()
        logging.info("Чаты успешно обновлены.")
        return {"msg": "users updated succsessfully"}, 200
    except Exception as e:
        logging.error(f"Возникла ошибка при обновлении чато^ {e}.")
        return {"msg": f"Error during updating users: {e}"}, 500
