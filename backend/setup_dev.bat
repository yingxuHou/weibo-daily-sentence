@echo off
REM 微博每日一句 - 开发环境设置脚本

echo ========================================
echo 微博每日一句 - 开发环境设置
echo ========================================
echo.

REM 检查 Python
echo [1/5] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo.

REM 创建虚拟环境
echo [2/5] 创建 Python 虚拟环境...
if exist "venv" (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)
echo.

REM 激活虚拟环境
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 安装依赖
echo [4/5] 安装 Python 依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo.

REM 创建必要的目录
echo [5/5] 创建必要的目录...
if not exist "..\data\images" mkdir ..\data\images
if not exist "logs" mkdir logs
echo 目录创建完成
echo.

echo ========================================
echo 设置完成！
echo ========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件，配置 API 密钥
echo 2. 运行 start_dev.bat 启动开发服务器
echo 3. 运行 python test_services.py 测试服务
echo.
pause
