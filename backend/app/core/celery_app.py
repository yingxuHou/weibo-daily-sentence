from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "weibo_daily",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

celery_app.conf.beat_schedule = {
    'daily-publish-task': {
        'task': 'app.tasks.publish_tasks.daily_publish_task',
        'schedule': crontab(hour=8, minute=0),
    },
    'check-content-pool': {
        'task': 'app.tasks.content_tasks.check_content_pool_task',
        'schedule': crontab(hour=9, minute=0),
    },
}
