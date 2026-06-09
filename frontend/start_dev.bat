@echo off
REM 前端开发环境启动脚本

echo ========================================
echo 微博每日一句 - 前端开发服务器
echo ========================================
echo.

REM 检查 Node.js
echo [1/3] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Node.js 未安装或未添加到 PATH
    echo 请访问 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)
node --version
npm --version
echo.

REM 检查依赖
echo [2/3] 检查依赖...
if not exist "node_modules" (
    echo 依赖未安装，正在安装...
    npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo 依赖已安装
)
echo.

REM 启动开发服务器
echo [3/3] 启动开发服务器...
echo.
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000 (需先启动后端)
echo.
echo 按 Ctrl+C 停止服务器
echo.

npm run dev
