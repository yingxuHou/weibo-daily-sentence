# Weibo Daily Sentence - 微博每日一句鸡汤运营AI员工

基于现有150条文案库，通过AI配图+Logo水印，实现微博每日自动发布。

## 项目结构

```
onesentence-oneday/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py   # 配置管理
│   │   │   └── database.py # 数据库连接
│   │   ├── models/         # 数据模型
│   │   │   └── content.py  # Content和PublishLog模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # FastAPI应用入口
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试代码
│   ├── requirements.txt    # Python依赖
│   ├── .env.example        # 环境变量示例
│   └── alembic.ini         # Alembic配置
├── frontend/               # 前端代码（审核后台）
├── logo/                   # 企业Logo资源
├── data/                   # 数据目录
│   └── images/            # 生成的图片
├── logs/                   # 日志文件
├── static/                 # 静态资源
├── sentence.md             # 文案库（150条）
├── PRD.md                  # 产品需求文档
├── TODO.md                 # 任务清单
└── README.md               # 项目说明
```

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0
- **任务队列**: Celery + Redis
- **图像处理**: Pillow + NumPy
- **数据库迁移**: Alembic

### 前端
- **框架**: Vue 3 + Element Plus（待开发）

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- MySQL 8.0+
- Redis

### 2. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

必须配置的环境变量：
- `DATABASE_URL`: MySQL数据库连接
- `WEIBO_APP_KEY`: 微博开放平台App Key
- `WEIBO_APP_SECRET`: 微博开放平台App Secret
- `OPENAI_API_KEY`: OpenAI API密钥（用于图片生成）

### 4. 初始化数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE weibo_daily CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行数据库迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

## 核心功能

### 已完成 ✅
- [x] 项目基础架构搭建
- [x] 数据库模型设计
- [x] FastAPI应用框架
- [x] 配置管理系统

### 开发中 🚧
- [ ] 文案选择模块
- [ ] AI图片生成集成
- [ ] Logo水印添加
- [ ] 审核管理后台
- [ ] 微博API集成
- [ ] 定时发布功能

详见 [TODO.md](TODO.md)

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 添加新的API路由

1. 在 `app/api/` 创建路由文件
2. 在 `app/main.py` 中注册路由

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 运行测试

```bash
pytest tests/
```

## 部署

详见 [TODO.md](TODO.md) 第14项

## 许可证

Private Project

## 联系方式

项目负责人：[Your Name]
