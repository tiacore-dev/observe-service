# app_celery/__init__.py

from celery import Celery
from config import CeleryConfig


def create_celery_app(flask_app=None):
    celery = Celery(
        __name__,
        broker=CeleryConfig.CELERY_BROKER_URL,
        backend=CeleryConfig.CELERY_RESULT_BACKEND
    )
    celery.conf.update({
        'result_backend': CeleryConfig.CELERY_RESULT_BACKEND,
        'BROKER_CONNECTION_RETRY_ON_STARTUP': True
    })

    if flask_app:
        celery.conf.update(flask_app.config)
        TaskBase = celery.Task

        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery.Task = ContextTask

    celery.autodiscover_tasks(['app_celery.tasks'])
    return celery
