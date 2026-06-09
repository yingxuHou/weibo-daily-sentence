from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.publication_service import PublicationError, PublicationService
from loguru import logger


@celery_app.task(
    bind=True,
    name='app.tasks.publish_tasks.daily_publish_task',
    max_retries=3,
)
def daily_publish_task(self):
    """每日定时发布任务"""
    db = SessionLocal()
    try:
        if not settings.WEIBO_PUBLISH_ENABLED:
            logger.info("Daily Weibo publishing is disabled")
            return {"success": False, "message": "Weibo publishing is disabled"}

        publication = PublicationService(db)
        content_id = publication.next_content_id()
        if content_id is None:
            logger.warning("No approved content available for daily publish")
            return {"success": False, "message": "No approved content available"}

        result = publication.publish_content(content_id)
        logger.info(
            "Daily publish task completed: content {}, weibo_id {}",
            content_id,
            result.weibo_id,
        )

        return {
            "success": True,
            "content_id": content_id,
            "weibo_id": result.weibo_id,
        }
    except PublicationError as exc:
        logger.error("Daily publish task failed: {}", exc)
        if exc.retryable:
            raise self.retry(exc=exc, countdown=60)
        return {"success": False, "message": str(exc)}
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name='app.tasks.publish_tasks.publish_content_task',
    max_retries=3,
)
def publish_content_task(self, content_id: int):
    """发布指定内容的异步任务"""
    db = SessionLocal()
    try:
        result = PublicationService(db).publish_content(content_id)
        logger.info("Published content {}, weibo_id {}", content_id, result.weibo_id)

        return {
            "success": True,
            "content_id": content_id,
            "weibo_id": result.weibo_id
        }
    except PublicationError as exc:
        logger.error("Publish task failed for content {}: {}", content_id, exc)
        if exc.retryable:
            raise self.retry(exc=exc, countdown=60)
        return {"success": False, "message": str(exc)}
    finally:
        db.close()
