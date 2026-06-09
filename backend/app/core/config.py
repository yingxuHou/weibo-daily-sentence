from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENV: str = "development"

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Weibo API
    WEIBO_APP_KEY: str
    WEIBO_APP_SECRET: str
    WEIBO_REDIRECT_URI: str
    WEIBO_ACCESS_TOKEN: Optional[str] = None

    # AI Image Generation
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None  # 自定义 API 基础 URL（用于中转服务）
    OPENAI_IMAGE_MODEL: str = "dall-e-3"  # 默认模型，可以改为 image-2
    STABILITY_API_KEY: Optional[str] = None

    # Application
    APP_NAME: str = "Weibo Daily Sentence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Paths
    SENTENCE_FILE_PATH: str
    LOGO_DIR_PATH: str
    OUTPUT_DIR_PATH: str

    # Content Settings
    DAILY_PUBLISH_TIME: str = "08:00"
    CONTENT_POOL_WARNING_THRESHOLD: int = 5
    DUPLICATE_CHECK_DAYS: int = 30

    # Image Settings
    IMAGE_WIDTH: int = 1080
    IMAGE_HEIGHT: int = 1080
    LOGO_SIZE_RATIO: float = 0.13
    LOGO_MARGIN: int = 20
    BRIGHTNESS_THRESHOLD: int = 128

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
