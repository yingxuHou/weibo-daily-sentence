# 微博每日一句 - 前端审核管理后台

基于 Vue 3 + Element Plus 构建的内容审核管理系统。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **UI 库**: Element Plus
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **构建工具**: Vite 5

## 功能特性

✅ **数据概览** - 实时统计、快捷操作、最近发布记录
✅ **内容审核** - 卡片式展示、批量操作、图片预览
✅ **发布记录** - 完整日志、状态追踪、统计分析
✅ **系统设置** - 参数配置、API 管理

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

访问：http://localhost:3000

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

### 预览生产构建

```bash
npm run preview
# 或
yarn preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口
│   │   └── content.js    # 内容相关接口
│   ├── layout/           # 布局组件
│   │   └── index.vue     # 主布局
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── stores/           # Pinia 状态管理
│   │   └── content.js    # 内容状态
│   ├── utils/            # 工具函数
│   │   └── request.js    # Axios 封装
│   ├── views/            # 页面组件
│   │   ├── Dashboard.vue     # 数据概览
│   │   ├── ContentList.vue   # 内容审核
│   │   ├── PublishedList.vue # 发布记录
│   │   └── Settings.vue      # 系统设置
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index_new.html        # HTML 模板
├── package.json          # 依赖配置
├── vite.config.js        # Vite 配置
└── README.md             # 项目说明
```

## 页面说明

### 1. 数据概览 (`/dashboard`)

- 实时统计数据（待审核、已通过、已发布、成功率）
- 内容池预警提示
- 快捷操作（生成内容池、审核内容、查看记录）
- 最近发布记录表格

### 2. 内容审核 (`/content`)

- 卡片式网格展示内容
- 图片预览和详情查看
- 状态筛选（待审核、已通过、已拒绝）
- 操作按钮：
  - 生成图片（自动调用 AI + Logo 水印）
  - 审核通过/拒绝
  - 重新审核
  - 删除内容

### 3. 发布记录 (`/published`)

- 发布统计（总数、成功数、失败数、成功率）
- 完整发布日志表格
- 微博链接跳转
- 错误信息查看

### 4. 系统设置 (`/settings`)

- **基本设置**：发布时间、预警阈值、去重天数
- **图片设置**：尺寸、Logo 比例、边距、亮度阈值
- **API 配置**：API 密钥管理（提示在后端配置）
- **关于**：版本信息、功能特性

## API 对接

前端通过 Vite 代理转发请求到后端：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端地址
      changeOrigin: true
    }
  }
}
```

## 开发注意事项

### 1. 环境要求

- Node.js 16+
- npm 7+ 或 yarn 1.22+

### 2. 后端服务

确保后端服务已启动：
```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 跨域处理

通过 Vite 代理解决跨域问题，生产环境需配置 Nginx 或后端 CORS。

### 4. 图片路径

图片 URL 处理逻辑：
```javascript
function getImageUrl(url) {
  if (url && url.startsWith('/')) {
    return `http://localhost:8000${url}`
  }
  return url
}
```

生产环境需修改为实际域名。

## 样式设计

采用自定义 CSS 变量，与原设计稿保持一致：

```css
:root {
  --bg: #f5f7f8;           /* 背景色 */
  --panel: #ffffff;        /* 面板背景 */
  --text: #1b2623;         /* 文本色 */
  --green: #217a61;        /* 主色调 */
  --muted: #66746f;        /* 次要文本 */
  /* ... 更多颜色变量 */
}
```

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 常见问题

### 1. 安装依赖失败

尝试清除缓存：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 2. 代理不生效

检查后端是否启动，端口是否为 8000。

### 3. 图片无法显示

检查后端 `OUTPUT_DIR_PATH` 配置和静态文件服务。

## 待实现功能

- [ ] 批量审核操作
- [ ] 内容编辑功能
- [ ] 图片重新生成
- [ ] 敏感词高亮
- [ ] 导出发布报表
- [ ] 用户权限管理
- [ ] 深色模式

## 许可证

Private Project

---

**开发团队**: PUDOW 朴道健康水专家运营团队
