@echo off
REM 微博每日一句 - Celery Worker 启动脚本

echo ========================================
echo 微博每日一句 - Celery Worker
echo ========================================
echo.

REM 激活虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup_dev.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 启动 Celery Worker...
echo.
echo 注意: 需要先启动 Redis 服务
echo.

celery -A app.core.celery_app worker --loglevel=info --pool=solo

pause
