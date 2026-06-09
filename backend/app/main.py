from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import sys

from app.core.config import settings
from app.api import content, review, publish
from app.utils.exceptions import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="微博每日一句鸡汤运营AI员工 - 后端API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router, prefix="/api/content", tags=["Content Management"])
app.include_router(review.router, prefix="/api/review", tags=["Review Management"])
app.include_router(publish.router, prefix="/api/publish", tags=["Publish Management"])

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Weibo Daily Sentence API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/debug/sentence-file")
async def debug_sentence_file():
    """调试端点：检查 sentence.md 文件状态"""
    import os
    from pathlib import Path

    sentence_path = Path(settings.SENTENCE_FILE_PATH)

    return {
        "configured_path": settings.SENTENCE_FILE_PATH,
        "exists": sentence_path.exists(),
        "is_file": sentence_path.is_file() if sentence_path.exists() else False,
        "absolute_path": str(sentence_path.absolute()),
        "cwd": os.getcwd(),
        "backend_sentence_exists": Path("./sentence.md").exists(),
        "backend_sentence_abs": str(Path("./sentence.md").absolute()),
        "app_sentence_exists": Path("/app/sentence.md").exists() if os.path.exists("/app") else False,
        "listdir_cwd": os.listdir(".")[:20] if os.path.exists(".") else [],
        "listdir_app": os.listdir("/app")[:20] if os.path.exists("/app") else []
    }


@app.get("/debug/ai-config")
async def debug_ai_config():
    """调试端点：检查 AI 图片生成配置"""
    return {
        "openai_api_key_configured": bool(settings.OPENAI_API_KEY),
        "openai_api_key_prefix": settings.OPENAI_API_KEY[:10] + "..." if settings.OPENAI_API_KEY else None,
        "openai_api_base": settings.OPENAI_API_BASE,
        "openai_image_model": settings.OPENAI_IMAGE_MODEL,
        "output_dir_path": settings.OUTPUT_DIR_PATH,
        "stability_api_key_configured": bool(settings.STABILITY_API_KEY)
    }
