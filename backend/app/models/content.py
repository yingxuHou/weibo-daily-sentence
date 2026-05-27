from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ContentStatus(str, enum.Enum):
    """Content status enum"""
    PENDING = "待审核"
    APPROVED = "已通过"
    REJECTED = "已拒绝"
    PUBLISHED = "已发布"


class PublishStatus(str, enum.Enum):
    """Publish status enum"""
    SUCCESS = "成功"
    FAILED = "失败"


class Content(Base):
    """Content table model"""
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sentence_id = Column(Integer, nullable=False, comment="文案库序号(1-150)")
    text = Column(Text, nullable=False, comment="文案内容")
    image_url = Column(String(255), comment="图片URL")
    logo_version = Column(String(20), comment="logo版本(原色/反白)")
    status = Column(
        Enum(ContentStatus),
        default=ContentStatus.PENDING,
        nullable=False,
        comment="状态"
    )
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    reviewed_at = Column(DateTime, comment="审核时间")
    published_at = Column(DateTime, comment="发布时间")
    reviewer_id = Column(Integer, comment="审核人ID")
    reject_reason = Column(Text, comment="拒绝原因")


class PublishLog(Base):
    """Publish log table model"""
    __tablename__ = "publish_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    weibo_id = Column(String(50), comment="微博ID")
    status = Column(
        Enum(PublishStatus),
        nullable=False,
        comment="发布状态"
    )
    error_msg = Column(Text, comment="错误信息")
    published_at = Column(DateTime, server_default=func.now(), comment="发布时间")
