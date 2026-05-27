from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.sentence_service import SentenceService
from app.core.config import settings
from loguru import logger


@celery_app.task(name='app.tasks.content_tasks.check_content_pool_task')
def check_content_pool_task():
    """检查内容池状态并发出警告"""
    db = SessionLocal()
    try:
        sentence_service = SentenceService(db)
        status = sentence_service.get_content_pool_status()

        logger.info(f"Content pool status: {status}")

        if status['warning']:
            logger.warning(
                f"Content pool warning: only {status['approved']} approved contents remaining "
                f"(threshold: {settings.CONTENT_POOL_WARNING_THRESHOLD})"
            )
            return {
                "warning": True,
                "message": f"Low content pool: {status['approved']} approved contents",
                "status": status
            }

        return {
            "warning": False,
            "message": "Content pool is healthy",
            "status": status
        }

    except Exception as e:
        logger.error(f"Check content pool task failed: {e}")
        return {"success": False, "message": str(e)}
    finally:
        db.close()


@celery_app.task(name='app.tasks.content_tasks.generate_content_pool_task')
def generate_content_pool_task(count: int = 30):
    """生成内容池的异步任务"""
    db = SessionLocal()
    try:
        sentence_service = SentenceService(db)
        contents = sentence_service.generate_content_pool(count)

        logger.info(f"Generated {len(contents)} contents in content pool")

        return {
            "success": True,
            "count": len(contents),
            "content_ids": [c.id for c in contents]
        }

    except Exception as e:
        logger.error(f"Generate content pool task failed: {e}")
        return {"success": False, "message": str(e)}
    finally:
        db.close()
