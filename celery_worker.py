from app import create_app
from app_celery.celery_app import create_celery_app

print('RUNNING CELERY WORKER')

# Создаем экземпляр Flask-приложения
flask_app = create_app(config_name='Celery')

# Создаем экземпляр Celery с интеграцией Flask
celery = create_celery_app(flask_app)

if __name__ == '__main__':
    celery.start()
