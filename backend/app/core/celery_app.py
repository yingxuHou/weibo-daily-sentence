from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


def _daily_publish_schedule():
    try:
        hour, minute = settings.DAILY_PUBLISH_TIME.split(":", maxsplit=1)
        return crontab(hour=int(hour), minute=int(minute))
    except (TypeError, ValueError):
        raise ValueError(
            "DAILY_PUBLISH_TIME must use 24-hour HH:MM format"
        )

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
        'schedule': _daily_publish_schedule(),
    },
    'check-content-pool': {
        'task': 'app.tasks.content_tasks.check_content_pool_task',
        'schedule': crontab(hour=9, minute=0),
    },
}
