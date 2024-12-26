import logging
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.db_get import get_prompt
from app.openai_funcs.openai_funcs import chatgpt_analyze


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
    logging.info(
        f"Отображение страницы деталей анализа с analysis_id: {analysis_id}")
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
    logging.info(f"Тип данных сообщений: {type(messages)}")
    logging.info(f"Количество сообщений: {len(messages)}")

    logging.info(f"""Пользователь {
                 current_user} начал создание анализа с prompt_id: {prompt_id}""")

    if not prompt_id or not messages:
        logging.warning("Ошибка: отсутствует prompt_id или сообщения")
        return jsonify({'error': 'Prompt ID and messages are required'}), 400

    try:
        # Логика анализа
        prompt = get_prompt(prompt_id)
        result_text, tokens_input, tokens_output = chatgpt_analyze(
            prompt, messages)

        from app.database.managers.analysis_manager import AnalysisManager
        db_a = AnalysisManager()
        analysis_id = db_a.save_analysis_result(
            prompt_id, result_text, filters, tokens_input, tokens_output)
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
        logging.info(f"""Возвращаем {len(result['analyses'])} анализов из {
                     result['total_count']} доступных""")
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
        logging.info(f"Детали анализа с analysis_id: {
                     analysis_id} успешно получены")
        return jsonify(analysis), 200
    except Exception as e:
        logging.error(f"Ошибка при получении деталей анализа: {str(e)}")
        return jsonify({'error': str(e)}), 500


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

        prompt_data = [{"prompt_name": s[0], "prompt_id": s[2]}
                       for s in prompts]
        logging.info(f"Найдено {len(prompt_data)} промптов для пользователя")
        return jsonify(prompt_data=prompt_data), 200
    except Exception as e:
        logging.error(f"Ошибка при получении промптов: {str(e)}")
        return jsonify({'error': 'Failed to fetch prompts'}), 500
