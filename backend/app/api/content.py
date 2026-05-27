from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.content import Content, ContentStatus
from app.services.sentence_service import SentenceService
from app.services.image_service import ImageService
from app.services.logo_service import LogoService
from loguru import logger

router = APIRouter()


class ContentResponse(BaseModel):
    id: int
    sentence_id: int
    text: str
    image_url: Optional[str]
    logo_version: Optional[str]
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    published_at: Optional[datetime]
    reject_reason: Optional[str]

    class Config:
        from_attributes = True


class GenerateContentRequest(BaseModel):
    count: int = 30


class GenerateContentResponse(BaseModel):
    success: bool
    message: str
    count: int
    contents: List[ContentResponse]


@router.post("/generate", response_model=GenerateContentResponse)
async def generate_content_pool(
    request: GenerateContentRequest,
    db: Session = Depends(get_db)
):
    """生成内容池（选择文案并创建记录）"""
    try:
        sentence_service = SentenceService(db)
        contents = sentence_service.generate_content_pool(request.count)

        return GenerateContentResponse(
            success=True,
            message=f"Successfully generated {len(contents)} contents",
            count=len(contents),
            contents=[ContentResponse.from_orm(c) for c in contents]
        )
    except Exception as e:
        logger.error(f"Failed to generate content pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{content_id}/generate-image")
async def generate_image_for_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """为指定内容生成AI图片"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        image_service = ImageService()
        image_path = await image_service.generate_image(content.text, content_id)

        if not image_path:
            raise HTTPException(status_code=500, detail="Failed to generate image")

        content.image_url = image_path
        db.commit()

        return {
            "success": True,
            "message": "Image generated successfully",
            "image_url": image_path
        }
    except Exception as e:
        logger.error(f"Failed to generate image for content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{content_id}/add-watermark")
async def add_watermark_to_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """为指定内容添加Logo水印"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if not content.image_url:
        raise HTTPException(status_code=400, detail="Content has no image")

    try:
        logo_service = LogoService()
        final_path, logo_version = logo_service.process_content_image(content.image_url)

        content.image_url = final_path
        content.logo_version = logo_version
        db.commit()

        return {
            "success": True,
            "message": "Watermark added successfully",
            "image_url": final_path,
            "logo_version": logo_version
        }
    except Exception as e:
        logger.error(f"Failed to add watermark for content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{content_id}/process")
async def process_content_complete(
    content_id: int,
    db: Session = Depends(get_db)
):
    """完整处理内容（生成图片+添加水印）"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        image_service = ImageService()
        image_path = await image_service.generate_image(content.text, content_id)

        if not image_path:
            raise HTTPException(status_code=500, detail="Failed to generate image")

        logo_service = LogoService()
        final_path, logo_version = logo_service.process_content_image(image_path)

        content.image_url = final_path
        content.logo_version = logo_version
        db.commit()

        return {
            "success": True,
            "message": "Content processed successfully",
            "content": ContentResponse.from_orm(content)
        }
    except Exception as e:
        logger.error(f"Failed to process content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ContentResponse])
async def list_contents(
    status: Optional[ContentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取内容列表"""
    query = db.query(Content)

    if status:
        query = query.filter(Content.status == status)

    contents = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    return [ContentResponse.from_orm(c) for c in contents]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """获取单个内容详情"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return ContentResponse.from_orm(content)


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """删除内容"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    db.delete(content)
    db.commit()

    return {"success": True, "message": "Content deleted successfully"}


@router.get("/pool/status")
async def get_pool_status(db: Session = Depends(get_db)):
    """获取内容池状态"""
    sentence_service = SentenceService(db)
    status = sentence_service.get_content_pool_status()
    return status
