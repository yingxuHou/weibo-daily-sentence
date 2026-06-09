from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.content import Content, ContentStatus, PublishLog, PublishStatus
from app.core.config import settings
from app.publishers.weibo import WeiboPublisher
from app.services.publication_service import PublicationError, PublicationService
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
        result = PublicationService(db).publish_content(content.id)
        published_at = content.published_at or datetime.now()
        logger.info(
            "Published content {} to Weibo, weibo_id: {}",
            content.id,
            result.weibo_id,
        )
        return PublishResponse(
            success=True,
            message="Content published successfully",
            weibo_id=result.weibo_id,
            published_at=published_at
        )
    except PublicationError as exc:
        logger.error("Failed to publish content {}: {}", request.content_id, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


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
    db: Session = Depends(get_db)
):
    """手动触发定时发布任务"""
    content = db.query(Content).filter(
        Content.status == ContentStatus.APPROVED
    ).order_by(Content.reviewed_at.asc()).first()

    if not content:
        return {"success": False, "message": "No approved content available"}

    try:
        result = PublicationService(db).publish_content(content.id)
        logger.info(f"Scheduled publish completed for content {content.id}")
        return {
            "success": True,
            "message": "Content published successfully",
            "content_id": content.id,
            "weibo_id": result.weibo_id
        }
    except PublicationError as exc:
        logger.error("Scheduled publish failed: {}", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/weibo/config")
async def get_weibo_config():
    """Check readiness without exposing credentials."""
    publisher = WeiboPublisher()
    return {
        "publish_enabled": settings.WEIBO_PUBLISH_ENABLED,
        "credentials_configured": publisher.is_configured,
        "daily_publish_time": settings.DAILY_PUBLISH_TIME,
        "redirect_uri": settings.WEIBO_REDIRECT_URI,
    }


@router.get("/weibo/authorize-url")
async def get_weibo_authorize_url(state: Optional[str] = None):
    """Return the official OAuth authorization URL used during setup."""
    try:
        return {"authorize_url": WeiboPublisher().get_authorize_url(state)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


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
