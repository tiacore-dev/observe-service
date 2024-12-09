from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


manage_chats_bp = Blueprint('manage_chats', __name__)

@manage_chats_bp.route('/manage_chats', methods=['GET'])
def manage_chats():
    return render_template('manage_chats.html')

@manage_chats_bp.route('/api/chats', methods=['GET'])
@jwt_required()
def get_chats():
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    chats = chat_manager.get_all_chats()
    return jsonify([chat.to_dict() for chat in chats]), 200

@manage_chats_bp.route('/api/prompts', methods=['GET'])
@jwt_required()
def get_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    prompts = prompt_manager.get_all_prompts()
    return jsonify([prompt.to_dict() for prompt in prompts]), 200

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
