from flask import Blueprint, render_template, request, jsonify

from app.database.managers.prompt_manager import PromptManager  # Для работы с промптами

manage_chats_bp = Blueprint('manage_chats', __name__)

@manage_chats_bp.route('/manage_chats', methods=['GET'])
def manage_chats():
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    prompt_manager = PromptManager()
    chats = chat_manager.get_all_chats()
    prompts = prompt_manager.get_prompts()  # Предполагаем, что есть метод для получения всех промптов
    return render_template('manage_chats.html', chats=chats, prompts=prompts)

@manage_chats_bp.route('/update_chat_prompt', methods=['POST'])
def update_chat_prompt():
    data = request.json
    chat_id = data.get('chat_id')
    prompt_id = data.get('prompt_id')
    from app.database.managers.chat_manager import ChatManager
    if not chat_id or not prompt_id:
        return jsonify({'error': 'Invalid data'}), 400

    chat_manager = ChatManager()
    try:
        chat_manager.update_default_prompt(chat_id, prompt_id)
        return jsonify({'message': 'Default prompt updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500
