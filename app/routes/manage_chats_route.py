from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

manage_chats_bp = Blueprint('manage_chats', __name__)

# Настраиваем уровень логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@manage_chats_bp.route('/manage_chats', methods=['GET'])
def manage_chats():
    logging.info("Страница управления чатами запрошена")
    return render_template('manage_chats.html')

@manage_chats_bp.route('/api/chats', methods=['GET'])
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

@manage_chats_bp.route('/api/prompts', methods=['GET'])
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

@manage_chats_bp.route('/update_chat_prompt', methods=['POST'])
def update_chat_prompt():
    from app.database.managers.chat_manager import ChatManager
    data = request.json
    chat_id = data.get('chat_id')
    prompt_id = data.get('prompt_id')
    current_user = get_jwt_identity()
    
    logging.info(f"Пользователь {current_user} пытается обновить дефолтный промпт для чата {chat_id} на {prompt_id}")
    
    if not chat_id or not prompt_id:
        logging.warning(f"Некорректные данные для обновления: chat_id={chat_id}, prompt_id={prompt_id}")
        return jsonify({'error': 'Invalid data'}), 400

    chat_manager = ChatManager()
    try:
        chat_manager.update_default_prompt(chat_id, prompt_id)
        logging.info(f"Дефолтный промпт для чата {chat_id} успешно обновлён на {prompt_id}")
        return jsonify({'message': 'Default prompt updated successfully'})
    except ValueError as e:
        logging.warning(f"Ошибка обновления: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(f"Непредвиденная ошибка при обновлении дефолтного промпта: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500
