@echo off
REM 前端环境设置脚本

echo ========================================
echo 微博每日一句 - 前端环境设置
echo ========================================
echo.

REM 检查 Node.js
echo [1/2] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Node.js 未安装
    echo.
    echo 请访问以下网址下载安装 Node.js:
    echo https://nodejs.org/
    echo.
    echo 推荐安装 LTS 版本（16.x 或更高）
    pause
    exit /b 1
)

echo Node.js 版本:
node --version
echo npm 版本:
npm --version
echo.

REM 安装依赖
echo [2/2] 安装项目依赖...
echo 这可能需要几分钟时间...
echo.

npm install

if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败
    echo.
    echo 尝试以下解决方案:
    echo 1. 删除 node_modules 文件夹后重试
    echo 2. 使用 cnpm 或切换 npm 镜像源
    echo 3. 检查网络连接
    pause
    exit /b 1
)

echo.
echo ========================================
echo 设置完成！
echo ========================================
echo.
echo 下一步:
echo 1. 确保后端服务已启动 (backend/start_dev.bat)
echo 2. 运行 start_dev.bat 启动前端开发服务器
echo 3. 访问 http://localhost:3000
echo.
pause
