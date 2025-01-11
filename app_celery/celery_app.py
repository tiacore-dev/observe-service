from celery import Celery
from config import CeleryConfig


def create_celery_app(flask_app=None):
    celery = Celery(
        __name__,
        broker=CeleryConfig.CELERY_BROKER_URL,
        backend=CeleryConfig.result_backend
    )
    celery.conf.update(
        result_backend=CeleryConfig.result_backend,
        task_routes={
            'app_celery.tasks.schedule_tasks.analyze_task': {'queue': 'analyze_queue'},
            'app_celery.tasks.schedule_tasks.save_analysis_result_task': {'queue': 'save_queue'},
            'app_celery.tasks.schedule_tasks.send_analysis_result_task': {'queue': 'send_queue'},
            'app_celery.tasks.bot_tasks.add_text_task': {'queue': 'telegram_queue'},
            'app_celery.tasks.bot_tasks.add_file_task': {'queue': 'telegram_queue'},
        },
        task_default_queue='default',
    )

    # Автообнаружение задач
    celery.autodiscover_tasks(['app_celery.tasks'])

    if flask_app:
        celery.conf.update(flask_app.config)
        TaskBase = celery.Task

        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery.Task = ContextTask

    return celery


# Без Flask-приложения (используется для автообнаружения)
app = create_celery_app()
