# Weibo Daily Sentence - 微博每日一句鸡汤运营AI员工

基于现有150条文案库，通过AI配图+Logo水印，实现微博每日自动发布。

微博开放平台授权、自动发布配置和上线检查见
[WEIBO_PUBLISHING.md](WEIBO_PUBLISHING.md)。

![License](https://img.shields.io/badge/license-Private-red)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)

---

## 📖 项目概述

**微博每日一句**是一个自动化的社交媒体运营工具，专为微博平台设计。它能够：

- 📝 从 150 条精选文案中智能选择内容
- 🎨 使用 AI（DALL-E 3 / Stability AI）自动生成配图
- 🏷️ 智能添加企业 Logo 水印（根据背景亮度选择原色/反白）
- ✅ 提供人工审核流程确保内容质量
- ⏰ 每天定时自动发布到微博
- 📊 完整的发布日志和统计功能

---

## ✨ 核心功能

### ✅ 已完成

- [x] **后端框架搭建**（FastAPI + SQLAlchemy）
- [x] **数据库模型设计**（Content / PublishLog）
- [x] **文案选择模块**（支持去重、随机选择）
- [x] **AI 图片生成集成**（DALL-E 3 / Stability AI）
- [x] **Logo 水印功能**（智能亮度检测）
- [x] **审核管理 API**（通过/拒绝/重置）
- [x] **微博 API 集成**（OAuth 认证、发布）
- [x] **定时发布任务**（Celery + Redis）
- [x] **API 文档**（Swagger / ReDoc）
- [x] **部署配置**（Zeabur 支持）

### 🚧 开发中

- [ ] **审核管理后台**（Vue 3 + Element Plus）
- [ ] **敏感词过滤**
- [ ] **内容池预警通知**
- [ ] **数据统计看板**

详见 [TODO.md](TODO.md)

---

## 🚀 快速开始

### 方式一：使用启动脚本（推荐 Windows 用户）

```bash
cd backend
setup_dev.bat      # 设置开发环境
start_dev.bat      # 启动开发服务器
```

### 方式二：手动安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问服务

- **API 服务**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 配置

编辑 `backend/.env` 文件：

```env
# AI 图片生成（至少配置一个）
OPENAI_API_KEY=sk-...
# 或
STABILITY_API_KEY=sk-...

# 微博 API
WEIBO_APP_KEY=your_app_key
WEIBO_APP_SECRET=your_app_secret
WEIBO_ACCESS_TOKEN=your_token

# 文件路径
SENTENCE_FILE_PATH=D:/university/Pudow/onesentence-oneday/sentence.md
LOGO_DIR_PATH=D:/university/Pudow/onesentence-oneday/logo
OUTPUT_DIR_PATH=D:/university/Pudow/onesentence-oneday/data/images
```

---

## 📁 项目结构

```
onesentence-oneday/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── content.py  # 内容管理
│   │   │   ├── review.py   # 审核管理
│   │   │   └── publish.py  # 发布管理
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── sentence_service.py   # 文案选择
│   │   │   ├── image_service.py      # AI 图片生成
│   │   │   ├── logo_service.py       # Logo 水印
│   │   │   └── weibo_service.py      # 微博 API
│   │   ├── tasks/          # Celery 任务
│   │   └── main.py         # 应用入口
│   ├── test_services.py    # 服务测试
│   ├── setup_dev.bat       # 环境设置
│   ├── start_dev.bat       # 启动服务器
│   └── requirements.txt    # 依赖包
├── frontend/               # 前端代码（待开发）
├── logo/                   # 企业 Logo 资源
├── data/images/            # 生成的图片
├── sentence.md             # 文案库（150 条）
├── README.md               # 项目说明
├── DEVELOPMENT.md          # 开发指南
└── TODO.md                 # 任务清单
```

---

## 📡 API 使用示例

### 1. 生成内容池

```bash
POST /api/content/generate
{
  "count": 30
}
```

### 2. 处理内容（图片+水印）

```bash
POST /api/content/{content_id}/process
```

### 3. 审核内容

```bash
POST /api/review/{content_id}/review
{
  "approved": true,
  "reviewer_id": 1
}
```

### 4. 发布到微博

```bash
POST /api/publish/
{
  "content_id": 1
}
```

更多 API 详情请查看：http://localhost:8000/docs

---

## 🔄 工作流程

```
生成内容池 → AI 生成图片 → 添加 Logo 水印 → 人工审核 → 定时发布
```

1. **生成内容池**：从 150 条文案中随机选择 30 条（30 天内不重复）
2. **AI 生成图片**：根据文案使用 DALL-E 3 / Stability AI 生成 1080x1080 配图
3. **添加 Logo 水印**：智能检测背景亮度，自动选择原色/反白 Logo
4. **人工审核**：通过管理后台审核内容质量
5. **定时发布**：每天早上 8:00 自动发布到微博

---

## 🧪 测试

```bash
cd backend
python test_services.py
```

测试内容：
- ✅ 文案加载功能
- ✅ Logo 服务
- ✅ 配置验证
- ✅ API 密钥检查

---
## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0
- **任务队列**: Celery + Redis
- **图像处理**: Pillow + NumPy
- **AI 图片**: OpenAI DALL-E 3 / Stability AI
- **数据库迁移**: Alembic

### 前端（计划中）
- **框架**: Vue 3 + Element Plus
- **构建工具**: Vite

---

## 📚 文档

- [开发指南](DEVELOPMENT.md) - 详细的开发文档和 API 说明
- [产品需求](PRD.md) - 完整的产品需求文档
- [任务清单](TODO.md) - 项目进度和待办事项
- [部署配置](ZEABUR_SETUP.md) - Zeabur 部署说明

---

## 🚢 部署

### Zeabur 一键部署

项目已配置 Zeabur 部署支持：

1. 在 Zeabur 创建新服务
2. 连接 Git 仓库
3. 配置环境变量（参考 `.env.example`）
4. 自动构建和部署

详见 [ZEABUR_SETUP.md](ZEABUR_SETUP.md)

---

## 📊 项目进度

当前版本：**v1.0.0-beta**

- 后端开发进度：**80%**
  - ✅ 核心服务模块
  - ✅ API 接口
  - ✅ 异步任务
  - ⏳ 数据库集成（已搁置）

- 前端开发进度：**0%**
  - ⏳ 审核管理界面
  - ⏳ 内容展示
  - ⏳ 统计看板

---

## ⚠️ 注意事项

1. **数据库连接问题**：当前 Zeabur MySQL 连接存在网络问题，已暂时搁置数据库功能
2. **API 密钥**：使用前请确保配置至少一个 AI 图片生成 API（OpenAI 或 Stability AI）
3. **微博 API**：需要先在微博开放平台注册应用并获取 Access Token
4. **成本控制**：AI 图片生成按量计费，建议设置合理的使用限制

---

## 🐛 故障排查

### 文案加载失败
检查 `SENTENCE_FILE_PATH` 配置是否正确，确保文件存在。

### Logo 未显示
确保 `logo/` 目录下有以下文件：
- `PUDOW朴道健康水专家-原色.png`
- `PUDOW朴道健康水专家-反白.png`

### 图片生成失败
检查 `OPENAI_API_KEY` 或 `STABILITY_API_KEY` 是否正确配置。

### Celery 任务不执行
1. 确保 Redis 正在运行
2. 检查 Celery Worker 和 Beat 是否启动
3. 查看 Celery 日志排查问题

更多问题请查看 [DEVELOPMENT.md](DEVELOPMENT.md) 的故障排查章节。

---

## 📝 更新日志

### v1.0.0-beta (2025-06-02)
- ✅ 完成后端核心框架搭建
- ✅ 实现文案选择、图片生成、Logo 水印功能
- ✅ 集成微博 API
- ✅ 实现 Celery 异步任务和定时发布
- ✅ 提供完整的 REST API
- ✅ 添加测试脚本和开发文档

---

## 📄 许可证

Private Project - All Rights Reserved

---

## 👥 团队

项目负责人：PUDOW 朴道健康水专家运营团队

---

**⭐ 如果这个项目对你有帮助，请给它一个 Star！**
