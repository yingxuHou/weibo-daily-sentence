# 微博每日一句 - 前端快速开始指南

## 📋 前置要求

- ✅ Node.js 16+ 已安装
- ✅ 后端服务已启动（在 8000 端口）

## 🚀 快速开始（Windows）

### 方式一：使用启动脚本（推荐）

```bash
# 1. 设置环境（仅第一次）
setup.bat

# 2. 启动开发服务器
start_dev.bat
```

### 方式二：手动命令

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

## 🌐 访问地址

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📁 项目结构

```
frontend/
├── src/
│   ├── views/          # 页面
│   ├── api/            # API
│   ├── stores/         # 状态
│   └── router/         # 路由
├── package.json
└── vite.config.js
```

## 🎨 功能页面

1. **数据概览** (`/dashboard`) - 统计数据、快捷操作
2. **内容审核** (`/content`) - 卡片展示、审核操作
3. **发布记录** (`/published`) - 发布日志、统计
4. **系统设置** (`/settings`) - 配置管理

## ⚙️ 开发命令

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产构建
```

## 🔧 常见问题

### 依赖安装失败
```bash
rm -rf node_modules package-lock.json
npm install
```

### 后端连接失败
确保后端在 8000 端口运行：
```bash
cd ../backend
start_dev.bat
```

### 图片无法显示
检查后端 `OUTPUT_DIR_PATH` 配置

## 📚 更多文档

详见 [README.md](README.md)
