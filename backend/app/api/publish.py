from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.content import Content, ContentStatus, PublishLog, PublishStatus
from app.services.weibo_service import WeiboService
from loguru import logger

router = APIRouter()


class PublishRequest(BaseModel):
    content_id: int


class PublishResponse(BaseModel):
    success: bool
    message: str
    weibo_id: Optional[str] = None
    published_at: Optional[datetime] = None


@router.post("/", response_model=PublishResponse)
async def publish_content(
    request: PublishRequest,
    db: Session = Depends(get_db)
):
    """发布内容到微博"""
    content = db.query(Content).filter(Content.id == request.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.status != ContentStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Content is not approved (current status: {content.status})"
        )

    if not content.image_url:
        raise HTTPException(status_code=400, detail="Content has no image")

    try:
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
            raise HTTPException(status_code=500, detail="Failed to publish to Weibo")

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

        logger.info(f"Published content {content.id} to Weibo, weibo_id: {weibo_id}")

        return PublishResponse(
            success=True,
            message="Content published successfully",
            weibo_id=weibo_id,
            published_at=published_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish content {request.content_id}: {e}")
        publish_log = PublishLog(
            content_id=content.id,
            status=PublishStatus.FAILED,
            error_msg=str(e)
        )
        db.add(publish_log)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next")
async def get_next_publishable_content(db: Session = Depends(get_db)):
    """获取下一个可发布的内容"""
    content = db.query(Content).filter(
        Content.status == ContentStatus.APPROVED
    ).order_by(Content.reviewed_at.asc()).first()

    if not content:
        return {"message": "No approved content available for publishing"}

    return {
        "id": content.id,
        "text": content.text,
        "image_url": content.image_url,
        "reviewed_at": content.reviewed_at
    }


@router.post("/schedule")
async def schedule_daily_publish(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """手动触发定时发布任务"""
    content = db.query(Content).filter(
        Content.status == ContentStatus.APPROVED
    ).order_by(Content.reviewed_at.asc()).first()

    if not content:
        return {"success": False, "message": "No approved content available"}

    try:
        weibo_service = WeiboService()
        result = weibo_service.publish_status(content.text, content.image_url)

        if not result:
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

        logger.info(f"Scheduled publish completed for content {content.id}")

        return {
            "success": True,
            "message": "Content published successfully",
            "content_id": content.id,
            "weibo_id": weibo_id
        }

    except Exception as e:
        logger.error(f"Scheduled publish failed: {e}")
        return {"success": False, "message": str(e)}


@router.get("/logs")
async def get_publish_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取发布日志"""
    logs = db.query(PublishLog).order_by(
        PublishLog.published_at.desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": log.id,
            "content_id": log.content_id,
            "weibo_id": log.weibo_id,
            "status": log.status.value,
            "error_msg": log.error_msg,
            "published_at": log.published_at
        }
        for log in logs
    ]


@router.get("/stats")
async def get_publish_stats(db: Session = Depends(get_db)):
    """获取发布统计"""
    total_published = db.query(Content).filter(
        Content.status == ContentStatus.PUBLISHED
    ).count()

    success_count = db.query(PublishLog).filter(
        PublishLog.status == PublishStatus.SUCCESS
    ).count()

    failed_count = db.query(PublishLog).filter(
        PublishLog.status == PublishStatus.FAILED
    ).count()

    return {
        "total_published": total_published,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": round(success_count / (success_count + failed_count) * 100, 2) if (success_count + failed_count) > 0 else 0
    }
