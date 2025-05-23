from flask import Flask
from .login_route import login_bp
from .account_route import account_bp
from .prompt_route import prompt_bp
from .logs_route import logs_bp
from .analysis_route import analysis_bp
from .gateway_routes import gateway_bp
from .chats_route import chats_bp
from .api_route import api_bp
from .users_route import users_bp


def register_routes(app: Flask):
    app.register_blueprint(login_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(prompt_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(gateway_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(users_bp)
