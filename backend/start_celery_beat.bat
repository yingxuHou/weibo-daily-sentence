@echo off
REM 微博每日一句 - Celery Beat 启动脚本（定时任务调度器）

echo ========================================
echo 微博每日一句 - Celery Beat
echo ========================================
echo.

REM 激活虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup_dev.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 启动 Celery Beat（定时任务调度器）...
echo.
echo 注意: 需要先启动 Redis 服务和 Celery Worker
echo.
echo 定时任务:
echo - 每天 08:00 自动发布微博
echo - 每天 09:00 检查内容池状态
echo.

celery -A app.core.celery_app beat --loglevel=info

pause
