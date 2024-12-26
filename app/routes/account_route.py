import logging
from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity


account_bp = Blueprint('account', __name__)


@account_bp.route('/health', methods=['GET'])
def health_check():
    return "OK", 200


@account_bp.route('/account', methods=['GET'])
def account():
    return render_template('account.html')


@account_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        logging.info(f"Пользователь авторизован: {current_user}")
        return jsonify({"message": "Access granted"}), 200
    except Exception as e:
        logging.error(f"Ошибка авторизации: {str(e)}")
        return jsonify({"error": "Authorization failed"}), 401


@account_bp.route('/get_username', methods=['GET'])
@jwt_required()  # Требуется авторизация с JWT
def get_username():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200
