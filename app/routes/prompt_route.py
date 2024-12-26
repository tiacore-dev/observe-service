import logging
from flask import Blueprint, request, redirect, url_for, jsonify, flash, render_template
from flask_jwt_extended import jwt_required


prompt_bp = Blueprint('prompt', __name__)


# Отображение страницы управления промптами
@prompt_bp.route('/manage_prompts', methods=['GET'])
def manage_prompts():
    return render_template('prompt/manage_prompts.html')

# Страница добавления нового промпта


@prompt_bp.route('/add_prompts', methods=['GET'])
def add_prompt_page():
    return render_template('prompt/add_prompt.html')

# Страница редактирования промпта


@prompt_bp.route('/prompt/<prompt_id>/', methods=['GET'])
def edit_prompt_page(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()

    prompt = prompt_manager.get_prompt_by_prompt_id(prompt_id)

    if prompt:
        return render_template('prompt/edit_prompt.html', prompt_id=prompt_id, prompt_name=prompt['prompt_name'], prompt_text=prompt['text'])
    else:
        flash('Prompt not found', 'danger')
        return redirect(url_for('prompt.manage_prompts'))

# Страница просмотра промпта


@prompt_bp.route('/prompt/<prompt_id>/view', methods=['GET'])
def view_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()

    prompt = prompt_manager.get_prompt_by_prompt_id(prompt_id)

    if prompt:
        return render_template('prompt/view_prompt.html', prompt_id=prompt_id, prompt_name=prompt['prompt_name'], prompt_text=prompt['text'])
    else:
        flash('Prompt not found', 'danger')
        return redirect(url_for('prompt.manage_prompts'))


# Достать все промпты
@prompt_bp.route('/prompt/all', methods=['GET'])
@jwt_required()
def get_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()

    logging.info(f"Загрузка страницы управления промптами для пользователя")
    prompts = prompt_manager.get_prompts()

    prompt_data = []

    for s in prompts:
        prompt_info = {
            "prompt_name": s[0],
            "text": s[1],
            "prompt_id": s[2],
            "use_automatic": s[3]
        }

        logging.info(
            f"Загрузка страницы управления промптами для пользователя: {prompt_info}")
        prompt_data.append(prompt_info)

    return jsonify(prompt_data=prompt_data), 200

# Добавление нового промпта


@prompt_bp.route('/prompt/add', methods=['POST'])
@jwt_required()
def add_prompt():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    data = request.json
    prompt_name = data['prompt_name']
    text = data['text']
    try:
        logging.info(f"Добавление нового промпта: Название: {prompt_name}")
        prompt_id = prompt_manager.add_prompt(prompt_name, text)
        flash('Prompt added successfully', 'success')
    except Exception as e:
        logging.error(f"Ошибка при добавлении промпта: {e}")
        flash('An error occurred while adding the prompt', 'danger')
    return jsonify({"message": "Prompt added successfully", "prompt_id": prompt_id}), 200


# Удаление промпта
@prompt_bp.route('/prompt/<prompt_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()

    try:
        logging.info(f"Удаление промпта {prompt_id}")
        prompt_manager.delete_prompt(prompt_id)
        logging.info(f"Промпт {prompt_id} удален")
        return jsonify(success=True, message='Prompt deleted successfully'), 200
    except Exception as e:
        logging.error(f"Ошибка при удалении промпта: {e}")
        return jsonify(success=False, message='An error occurred while deleting the prompt'), 500


# Редактирование существующего промпта
@prompt_bp.route('/prompt/<prompt_id>/edit', methods=['PATCH'])
@jwt_required()
def edit_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    data = request.get_json()
    new_text = data.get('text')
    new_prompt_name = data.get('prompt_name')  # Получаем новое имя промпта

    try:
        logging.info(f"Изменение промпта {prompt_id}")
        success = prompt_manager.edit_prompt(
            prompt_id, new_text, new_prompt_name)  # Передаем новое имя

        if success:
            logging.info(f"Промпт {prompt_id} изменен")
            return jsonify(success=True, message='Prompt updated successfully'), 200
        else:
            logging.error(f"Промпт {prompt_id} не найден или произошла ошибка")
            return jsonify(success=False, message='Prompt ID not found'), 400

    except Exception as e:
        logging.error(f"Ошибка при изменении промпта: {e}")
        return jsonify(success=False, message=str(e)), 500


@prompt_bp.route('/prompt/<prompt_id>/set_automatic', methods=['PATCH'])
@jwt_required()
def set_automatic(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    data = request.get_json()
    use_automatic = data.get('use_automatic')
    logging.info(f"""Запрос на изменение флага 'use_automatic' для промпта {
                 prompt_id}: {use_automatic}""")
    try:
        # Сначала сбрасываем флаг для всех остальных промптов, если устанавливаем новый флаг
        if use_automatic:
            logging.info(f"Сброс флага 'use_automatic' для всех промптов.")
            prompt_manager.reset_automatic_flag()  # Функция для сброса флага
        # Обновляем выбранный промпт
        prompt_manager.set_automatic_flag(prompt_id, use_automatic)

        logging.info(f"""Флаг 'use_automatic' для промпта {
                     prompt_id} успешно обновлён на {use_automatic}.""")
        return jsonify(success=True, message='Automatic flag updated successfully'), 200
    except Exception as e:
        logging.error(f"Ошибка при изменении флага: {e}")
        return jsonify(success=False, message=str(e)), 500


@prompt_bp.route('/get_automatic_prompt', methods=['GET'])
@jwt_required()
def get_automatic_prompt():
    """
    Возвращает промпт, у которого установлен флаг use_automatic.
    """
    try:
        from app.database.managers.prompt_manager import PromptManager
        prompt_manager = PromptManager()

        # Получение промпта с установленным флагом use_automatic
        automatic_prompt = prompt_manager.get_automatic_prompt()

        if automatic_prompt:
            logging.info("Автоматический промпт успешно найден.")
            return jsonify(automatic_prompt), 200
        else:
            logging.info("Автоматический промпт не найден.")
            return jsonify({"msg": "No automatic prompt found"}), 404
    except Exception as e:
        logging.error(
            f"Ошибка при получении автоматического промпта: {str(e)}")
        return jsonify({"error": "Failed to fetch automatic prompt"}), 500
