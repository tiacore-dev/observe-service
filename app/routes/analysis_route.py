from flask import Blueprint, request, jsonify, render_template
from app.utils.db_get import get_prompt
from app.openai_funcs.openai_funcs import chatgpt_analyze
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

analysis_bp = Blueprint('analysis', __name__)

# Отображение страницы для создания анализа
@analysis_bp.route('/analysis', methods=['GET'])
def transcription():
    logging.info("Отображение страницы создания анализа")
    return render_template('analysis/analysis.html')

# Отображение страницы результатов анализа
@analysis_bp.route('/analysis_result', methods=['GET'])
def analysis_result():
    logging.info("Отображение страницы результатов анализа")
    return render_template('analysis/analysis_result.html')

# Отображение страницы деталей анализа
@analysis_bp.route('/analysis/<analysis_id>/view', methods=['GET'])
def get_analysis_by_analysis_id(analysis_id):
    logging.info(f"Отображение страницы деталей анализа с analysis_id: {analysis_id}")
    return render_template('analysis/analysis_details.html', analysis_id=analysis_id)

# Создание нового анализа
@analysis_bp.route('/analysis/create', methods=['POST'])
@jwt_required()
def create_analysis():
    data = request.json
    prompt_id = data.get('prompt_id')
    messages = data.get('messages')
    filters = data.get('filters')
    current_user = get_jwt_identity()

    logging.info(f"Пользователь {current_user} начал создание анализа с prompt_id: {prompt_id}")

    if not prompt_id or not messages:
        logging.warning("Ошибка: отсутствует prompt_id или сообщения")
        return jsonify({'error': 'Prompt ID and messages are required'}), 400

    try:
        # Логика анализа
        result_text, tokens = chatgpt_analyze(prompt_id, messages)

        from app.database.managers.analysis_manager import AnalysisManager
        db_a = AnalysisManager()
        analysis_id = db_a.save_analysis_result(prompt_id, result_text, filters, tokens)
        logging.info(f"Анализ успешно сохранен с analysis_id: {analysis_id}")

        return jsonify({
            'message': 'Анализ успешно создан!',
            'analysis_id': analysis_id,
            'result_text': result_text
        }), 201
    except Exception as e:
        logging.error(f"Ошибка при создании анализа: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Получение списка анализов
@analysis_bp.route('/analysis/all', methods=['GET'])
@jwt_required()
def get_analyses():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    logging.info(f"Запрос списка анализов с offset={offset}, limit={limit}")
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    try:
        result = db.get_analysis_all(offset=offset, limit=limit)
        logging.info(f"Возвращаем {len(result['analyses'])} анализов из {result['total_count']} доступных")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Ошибка при получении списка анализов: {str(e)}")
        return jsonify({'error': 'Failed to fetch analyses'}), 500

# Получение деталей анализа
@analysis_bp.route('/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_detail(analysis_id):
    logging.info(f"Запрос деталей анализа с analysis_id: {analysis_id}")
    from app.database.managers.analysis_manager import AnalysisManager
    db_a = AnalysisManager()
    try:
        analysis = db_a.get_analysis_by_id(analysis_id)
        if not analysis:
            logging.warning(f"Анализ с analysis_id: {analysis_id} не найден")
            return jsonify({'error': 'Analysis not found'}), 404
        logging.info(f"Детали анализа с analysis_id: {analysis_id} успешно получены")
        return jsonify(analysis), 200
    except Exception as e:
        logging.error(f"Ошибка при получении деталей анализа: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Получение сообщений с фильтрацией
@analysis_bp.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    logging.info(f"Запрос сообщений с фильтрацией: start_date={start_date}, end_date={end_date}, user_id={user_id}, chat_id={chat_id}")

    from app.database.managers.message_manager import MessageManager
    manager = MessageManager()
    try:
        messages = manager.get_filtered_messages(start_date=start_date, end_date=end_date, user_id=user_id, chat_id=chat_id)
        total_messages = len(messages)
        paginated_messages = messages[(page - 1) * page_size:page * page_size]

        logging.info(f"Найдено {len(messages)} сообщений, возвращено {len(paginated_messages)} сообщений на странице {page}")
        return jsonify({
            'total': total_messages,
            'page': page,
            'page_size': page_size,
            'messages': [msg.to_dict() for msg in paginated_messages],
        }), 200
    except Exception as e:
        logging.error(f"Ошибка при фильтрации сообщений: {str(e)}")
        return jsonify({'error': 'Failed to fetch messages'}), 500


# Получение пользовательских промптов
@analysis_bp.route('/user_prompts', methods=['GET'])
@jwt_required()
def get_user_prompts():
    logging.info("Запрос списка промптов для пользователя")
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    try:
        prompts = prompt_manager.get_prompts()
        if not prompts:
            logging.warning("Промпты для пользователя не найдены")
            return jsonify({"msg": "No prompts found"}), 404

        prompt_data = [{"prompt_name": s[0], "prompt_id": s[2]} for s in prompts]
        logging.info(f"Найдено {len(prompt_data)} промптов для пользователя")
        return jsonify(prompt_data=prompt_data), 200
    except Exception as e:
        logging.error(f"Ошибка при получении промптов: {str(e)}")
        return jsonify({'error': 'Failed to fetch prompts'}), 500


@analysis_bp.route('/api/chats', methods=['GET'])
@jwt_required()
def get_chats():
    """
    Возвращает список доступных чатов
    """
    from app.database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    try:
        chats = chat_manager.get_all_chats()
        return jsonify([{"chat_id": chat.chat_id, "chat_name": chat.chat_name or "Без названия"} for chat in chats]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch chats'}), 500