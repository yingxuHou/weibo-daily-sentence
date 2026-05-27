# Zeabur 部署指南

## 前置条件

1. 已在Zeabur创建MySQL服务
2. 已将代码推送到GitHub仓库：https://github.com/yingxuHou/weibo-daily-sentence.git

## 部署步骤

### 1. 在Zeabur创建新服务

1. 登录 [Zeabur控制台](https://zeabur.com)
2. 选择你的项目
3. 点击 "Add Service" → "Git Repository"
4. 选择 `yingxuHou/weibo-daily-sentence` 仓库
5. 设置根目录为 `backend`

### 2. 配置环境变量

在Zeabur服务的 "Variables" 页面添加以下环境变量：

#### 必需配置

```bash
# 环境
ENV=production

# 数据库 - 使用Zeabur MySQL服务的引用
DATABASE_URL=${MYSQL_URL}

# 或者手动配置（如果上面的引用不工作）
# DATABASE_URL=mysql+pymysql://root:N81P265Ru7ODZkp0VQz943GMibgExJqK@mysql.zeabur.internal:3306/zeabur?charset=utf8mb4

DB_ECHO=False

# Redis（如果需要）
REDIS_URL=redis://localhost:6379/0

# 微博API（需要从微博开放平台获取）
WEIBO_APP_KEY=your_app_key_here
WEIBO_APP_SECRET=your_app_secret_here
WEIBO_REDIRECT_URI=https://your-domain.zeabur.app/callback
WEIBO_ACCESS_TOKEN=your_access_token_here

# AI图片生成API
OPENAI_API_KEY=your_openai_key_here

# 应用设置
APP_NAME=Weibo Daily Sentence
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# 文件路径（容器内路径）
SENTENCE_FILE_PATH=/app/sentence.md
LOGO_DIR_PATH=/app/logo
OUTPUT_DIR_PATH=/app/data/images

# 内容设置
DAILY_PUBLISH_TIME=08:00
CONTENT_POOL_WARNING_THRESHOLD=5
DUPLICATE_CHECK_DAYS=30

# 图片设置
IMAGE_WIDTH=1080
IMAGE_HEIGHT=1080
LOGO_SIZE_RATIO=0.13
LOGO_MARGIN=20
BRIGHTNESS_THRESHOLD=128
```

### 3. 连接MySQL服务

Zeabur支持服务间引用，推荐使用以下方式：

#### 方法A：使用服务引用（推荐）
```bash
DATABASE_URL=${MYSQL_URL}
```

Zeabur会自动将 `${MYSQL_URL}` 替换为内部MySQL连接地址。

#### 方法B：手动配置内部地址
如果方法A不工作，使用MySQL服务的内部地址：
```bash
DATABASE_URL=mysql+pymysql://root:N81P265Ru7ODZkp0VQz943GMibgExJqK@<mysql-service-name>.zeabur.internal:3306/zeabur?charset=utf8mb4
```

**注意**：将 `<mysql-service-name>` 替换为你的MySQL服务名称。

### 4. 初始化数据库

部署成功后，需要运行数据库迁移：

1. 在Zeabur控制台找到你的服务
2. 进入 "Logs" 或 "Terminal"
3. 运行：
```bash
alembic upgrade head
```

或者在本地连接到Zeabur数据库运行迁移（需要先配置IP白名单）。

### 5. 验证部署

访问：`https://your-service.zeabur.app/docs`

应该能看到FastAPI的Swagger文档页面。

## 自动部署

配置完成后，每次推送到GitHub的main分支，Zeabur会自动：
1. 拉取最新代码
2. 构建Docker镜像
3. 重启服务

## 故障排查

### 数据库连接失败

1. 检查 `DATABASE_URL` 格式是否正确
2. 确认使用的是内部地址，不是公网IP
3. 检查MySQL服务是否正常运行
4. 查看服务日志：Zeabur控制台 → 服务 → Logs

### 文件路径问题

容器内的路径与本地不同：
- 本地：`D:/university/Pudow/onesentence-oneday/sentence.md`
- 容器：`/app/sentence.md`

确保环境变量使用容器内路径。

### 查看日志

在Zeabur控制台：
1. 选择你的服务
2. 点击 "Logs" 标签
3. 查看实时日志输出

## 下一步

1. 配置自定义域名
2. 设置定时任务（Cron Job）用于每日发布
3. 配置Redis服务（如果需要Celery任务队列）
4. 添加监控和告警

## 相关链接

- Zeabur文档：https://zeabur.com/docs
- 项目仓库：https://github.com/yingxuHou/weibo-daily-sentence
- FastAPI文档：https://fastapi.tiangolo.com
