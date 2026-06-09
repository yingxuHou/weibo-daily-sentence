from typing import Dict, Optional

from loguru import logger

from app.publishers.weibo import (
    WeiboAPIError,
    WeiboConfigurationError,
    WeiboPublisher,
)


class WeiboService(WeiboPublisher):
    """Backward-compatible facade for older call sites."""

    def get_access_token(self, code: str) -> Optional[Dict]:
        try:
            return self.exchange_code(code)
        except (WeiboAPIError, WeiboConfigurationError) as exc:
            logger.error("Failed to get Weibo access token: {}", exc)
            return None

    def publish_status(self, text: str, image_path: Optional[str] = None) -> Optional[Dict]:
        try:
            return self.publish(text, image_path).raw
        except (WeiboAPIError, WeiboConfigurationError, ValueError) as exc:
            logger.error("Failed to publish Weibo status: {}", exc)
            return None

    def delete_status(self, weibo_id: str) -> bool:
        try:
            return self.delete(weibo_id)
        except (WeiboAPIError, WeiboConfigurationError) as exc:
            logger.error("Failed to delete Weibo status {}: {}", weibo_id, exc)
            return False
