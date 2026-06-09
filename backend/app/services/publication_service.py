from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.content import Content, ContentStatus, PublishLog, PublishStatus
from app.publishers.weibo import (
    WeiboAPIError,
    WeiboConfigurationError,
    WeiboPublishResult,
    WeiboPublisher,
)


class PublicationError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class PublicationService:
    """Coordinates one content record, one platform call, and its audit log."""

    def __init__(
        self,
        db: Session,
        publisher: Optional[WeiboPublisher] = None,
    ):
        self.db = db
        self.publisher = publisher or WeiboPublisher()

    def publish_content(self, content_id: int) -> WeiboPublishResult:
        content = (
            self.db.query(Content)
            .filter(Content.id == content_id)
            .with_for_update()
            .first()
        )
        if not content:
            raise PublicationError("Content not found")
        if content.status != ContentStatus.APPROVED.value:
            raise PublicationError(
                f"Content is not approved (current status: {content.status})"
            )
        if not content.image_url:
            raise PublicationError("Content has no image")

        try:
            result = self.publisher.publish(content.text, content.image_url)
        except (WeiboAPIError, WeiboConfigurationError, ValueError) as exc:
            self._record_failure(content.id, str(exc))
            raise PublicationError(
                str(exc),
                retryable=getattr(exc, "retryable", False),
            ) from exc

        published_at = datetime.now()
        content.status = ContentStatus.PUBLISHED.value
        content.published_at = published_at
        self.db.add(
            PublishLog(
                content_id=content.id,
                weibo_id=result.weibo_id,
                status=PublishStatus.SUCCESS.value,
                published_at=published_at,
            )
        )
        self.db.commit()
        return result

    def next_content_id(self) -> Optional[int]:
        content = (
            self.db.query(Content)
            .filter(Content.status == ContentStatus.APPROVED.value)
            .order_by(Content.reviewed_at.asc())
            .first()
        )
        return content.id if content else None

    def _record_failure(self, content_id: int, message: str) -> None:
        self.db.add(
            PublishLog(
                content_id=content_id,
                status=PublishStatus.FAILED.value,
                error_msg=message,
            )
        )
        self.db.commit()
