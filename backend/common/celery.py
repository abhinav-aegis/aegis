from celery import Celery
from backend.common.config import settings

celery_app = Celery(
    "aegis_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_routes={
        "tasks.agents.*": {"queue": "agents"},
        "tasks.pipelines.*": {"queue": "pipelines"},
    },
)

@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
