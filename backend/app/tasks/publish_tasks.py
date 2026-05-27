from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.content import Content, ContentStatus, PublishLog, PublishStatus
from app.services.weibo_service import WeiboService
from datetime import datetime
from loguru import logger


@celery_app.task(name='app.tasks.publish_tasks.daily_publish_task')
def daily_publish_task():
    """每日定时发布任务"""
    db = SessionLocal()
    try:
        content = db.query(Content).filter(
            Content.status == ContentStatus.APPROVED
        ).order_by(Content.reviewed_at.asc()).first()

        if not content:
            logger.warning("No approved content available for daily publish")
            return {"success": False, "message": "No approved content available"}

        if not content.image_url:
            logger.error(f"Content {content.id} has no image")
            return {"success": False, "message": "Content has no image"}

        weibo_service = WeiboService()
        result = weibo_service.publish_status(content.text, content.image_url)

        if not result:
            publish_log = PublishLog(
                content_id=content.id,
                status=PublishStatus.FAILED,
                error_msg="Failed to publish to Weibo"
            )
            db.add(publish_log)
            db.commit()
            logger.error(f"Failed to publish content {content.id}")
            return {"success": False, "message": "Failed to publish to Weibo"}

        weibo_id = str(result.get('id'))
        published_at = datetime.now()

        content.status = ContentStatus.PUBLISHED
        content.published_at = published_at

        publish_log = PublishLog(
            content_id=content.id,
            weibo_id=weibo_id,
            status=PublishStatus.SUCCESS,
            published_at=published_at
        )
        db.add(publish_log)
        db.commit()

        logger.info(f"Daily publish task completed: content {content.id}, weibo_id {weibo_id}")

        return {
            "success": True,
            "content_id": content.id,
            "weibo_id": weibo_id,
            "published_at": published_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Daily publish task failed: {e}")
        return {"success": False, "message": str(e)}
    finally:
        db.close()


@celery_app.task(name='app.tasks.publish_tasks.publish_content_task')
def publish_content_task(content_id: int):
    """发布指定内容的异步任务"""
    db = SessionLocal()
    try:
        content = db.query(Content).filter(Content.id == content_id).first()

        if not content:
            logger.error(f"Content {content_id} not found")
            return {"success": False, "message": "Content not found"}

        if content.status != ContentStatus.APPROVED:
            logger.error(f"Content {content_id} is not approved")
            return {"success": False, "message": "Content is not approved"}

        if not content.image_url:
            logger.error(f"Content {content_id} has no image")
            return {"success": False, "message": "Content has no image"}

        weibo_service = WeiboService()
        result = weibo_service.publish_status(content.text, content.image_url)

        if not result:
            publish_log = PublishLog(
                content_id=content.id,
                status=PublishStatus.FAILED,
                error_msg="Failed to publish to Weibo"
            )
            db.add(publish_log)
            db.commit()
            return {"success": False, "message": "Failed to publish to Weibo"}

        weibo_id = str(result.get('id'))
        published_at = datetime.now()

        content.status = ContentStatus.PUBLISHED
        content.published_at = published_at

        publish_log = PublishLog(
            content_id=content.id,
            weibo_id=weibo_id,
            status=PublishStatus.SUCCESS,
            published_at=published_at
        )
        db.add(publish_log)
        db.commit()

        logger.info(f"Published content {content_id}, weibo_id {weibo_id}")

        return {
            "success": True,
            "content_id": content_id,
            "weibo_id": weibo_id
        }

    except Exception as e:
        logger.error(f"Publish task failed for content {content_id}: {e}")
        return {"success": False, "message": str(e)}
    finally:
        db.close()
