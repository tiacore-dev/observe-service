from flask import Flask
from .login_route import login_bp
from .account_route import account_bp
from .prompt_route import prompt_bp
from .logs_route import logs_bp
from .analysis_route import analysis_bp
from .gateway_routes import gateway_bp
from .manage_chats_route import manage_chats_bp





def register_routes(app: Flask):
    app.register_blueprint(login_bp)  
    app.register_blueprint(account_bp)
    app.register_blueprint(prompt_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(gateway_bp)
    app.register_blueprint(manage_chats_bp)

