@echo off
REM 微博每日一句 - 开发环境启动脚本

echo ========================================
echo 微博每日一句 - 开发服务器
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup_dev.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 启动 FastAPI 服务器
echo [2/2] 启动 FastAPI 开发服务器...
echo.
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
