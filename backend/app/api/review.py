from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.content import Content, ContentStatus
from loguru import logger

router = APIRouter()


class ReviewRequest(BaseModel):
    approved: bool
    reject_reason: Optional[str] = None
    reviewer_id: Optional[int] = None


class ReviewResponse(BaseModel):
    success: bool
    message: str
    content_id: int
    status: str


@router.post("/{content_id}/review", response_model=ReviewResponse)
async def review_content(
    content_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    """审核内容"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 使用字符串值比较，因为数据库中存储的是字符串
    if content.status != ContentStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail=f"Content is not pending review (current status: {content.status})"
        )

    try:
        if request.approved:
            content.status = ContentStatus.APPROVED.value
            content.reviewed_at = datetime.now()
            content.reviewer_id = request.reviewer_id
            message = "Content approved"
        else:
            content.status = ContentStatus.REJECTED.value
            content.reviewed_at = datetime.now()
            content.reviewer_id = request.reviewer_id
            content.reject_reason = request.reject_reason or "No reason provided"
            message = "Content rejected"

        db.commit()
        logger.info(f"Content {content_id} reviewed: {content.status}")

        return ReviewResponse(
            success=True,
            message=message,
            content_id=content_id,
            status=content.status
        )
    except Exception as e:
        logger.error(f"Failed to review content {content_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/count")
async def get_pending_count(db: Session = Depends(get_db)):
    """获取待审核内容数量"""
    count = db.query(Content).filter(Content.status == ContentStatus.PENDING.value).count()
    return {"pending_count": count}


@router.get("/approved/count")
async def get_approved_count(db: Session = Depends(get_db)):
    """获取已通过内容数量"""
    count = db.query(Content).filter(Content.status == ContentStatus.APPROVED.value).count()
    return {"approved_count": count}


@router.post("/{content_id}/reset")
async def reset_review_status(
    content_id: int,
    db: Session = Depends(get_db)
):
    """重置审核状态（重新提交审核）"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.status == ContentStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=400,
            detail="Cannot reset published content"
        )

    try:
        content.status = ContentStatus.PENDING.value
        content.reviewed_at = None
        content.reviewer_id = None
        content.reject_reason = None
        db.commit()

        logger.info(f"Content {content_id} review status reset")
        return {
            "success": True,
            "message": "Review status reset successfully",
            "content_id": content_id
        }
    except Exception as e:
        logger.error(f"Failed to reset review status for content {content_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
