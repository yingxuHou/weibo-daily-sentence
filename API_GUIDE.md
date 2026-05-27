# Weibo Daily Sentence Backend - API 使用指南

## 基础信息

- **Base URL**: `http://your-server-ip:8000`
- **API文档**: `http://your-server-ip:8000/docs`
- **健康检查**: `GET /health`

---

## 1. 内容管理 API

### 1.1 生成内容池

**POST** `/api/content/generate`

生成指定数量的内容（从文案库随机选择）

**请求体**:
```json
{
  "count": 30
}
```

**响应**:
```json
{
  "success": true,
  "message": "Successfully generated 30 contents",
  "count": 30,
  "contents": [...]
}
```

### 1.2 获取内容列表

**GET** `/api/content/`

**查询参数**:
- `status`: 过滤状态（pending/approved/rejected/published）
- `skip`: 跳过数量（默认0）
- `limit`: 返回数量（默认50，最大100）

**响应**:
```json
[
  {
    "id": 1,
    "sentence_id": 42,
    "text": "新的一天，不是重复昨天...",
    "image_url": "/data/images/content_1_xxx.png",
    "logo_version": "color",
    "status": "pending",
    "created_at": "2024-01-01T08:00:00",
    "reviewed_at": null,
    "published_at": null,
    "reject_reason": null
  }
]
```

### 1.3 获取单个内容

**GET** `/api/content/{content_id}`

### 1.4 为内容生成图片

**POST** `/api/content/{content_id}/generate-image`

使用AI为指定内容生成图片

### 1.5 为内容添加水印

**POST** `/api/content/{content_id}/add-watermark`

为已有图片添加Logo水印

### 1.6 完整处理内容

**POST** `/api/content/{content_id}/process`

一键完成：生成图片 + 添加水印

### 1.7 删除内容

**DELETE** `/api/content/{content_id}`

### 1.8 获取内容池状态

**GET** `/api/content/pool/status`

**响应**:
```json
{
  "pending": 15,
  "approved": 8,
  "total": 23,
  "warning": false
}
```

---

## 2. 审核管理 API

### 2.1 审核内容

**POST** `/api/review/{content_id}/review`

**请求体**:
```json
{
  "approved": true,
  "reject_reason": "图片质量不佳",  // 拒绝时必填
  "reviewer_id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "Content approved",
  "content_id": 1,
  "status": "approved"
}
```

### 2.2 获取待审核数量

**GET** `/api/review/pending/count`

**响应**:
```json
{
  "pending_count": 15
}
```

### 2.3 获取已通过数量

**GET** `/api/review/approved/count`

**响应**:
```json
{
  "approved_count": 8
}
```

### 2.4 重置审核状态

**POST** `/api/review/{content_id}/reset`

将内容重新设为待审核状态

---

## 3. 发布管理 API

### 3.1 发布内容到微博

**POST** `/api/publish/`

**请求体**:
```json
{
  "content_id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "Content published successfully",
  "weibo_id": "4876543210987654",
  "published_at": "2024-01-01T08:00:00"
}
```

### 3.2 获取下一个可发布内容

**GET** `/api/publish/next`

返回最早审核通过的内容

### 3.3 手动触发定时发布

**POST** `/api/publish/schedule`

立即执行一次定时发布任务

### 3.4 获取发布日志

**GET** `/api/publish/logs`

**查询参数**:
- `skip`: 跳过数量（默认0）
- `limit`: 返回数量（默认50）

**响应**:
```json
[
  {
    "id": 1,
    "content_id": 1,
    "weibo_id": "4876543210987654",
    "status": "success",
    "error_msg": null,
    "published_at": "2024-01-01T08:00:00"
  }
]
```

### 3.5 获取发布统计

**GET** `/api/publish/stats`

**响应**:
```json
{
  "total_published": 100,
  "success_count": 98,
  "failed_count": 2,
  "success_rate": 98.0
}
```

---

## 4. 完整工作流程

### 4.1 初始化内容池

```bash
# 1. 生成30条内容
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 30}'

# 2. 为每条内容生成图片和水印
for id in {1..30}; do
  curl -X POST http://localhost:8000/api/content/$id/process
done
```

### 4.2 审核流程

```bash
# 1. 获取待审核列表
curl http://localhost:8000/api/content/?status=pending

# 2. 审核通过
curl -X POST http://localhost:8000/api/review/1/review \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "reviewer_id": 1}'

# 3. 审核拒绝
curl -X POST http://localhost:8000/api/review/2/review \
  -H "Content-Type: application/json" \
  -d '{"approved": false, "reject_reason": "图片不合适", "reviewer_id": 1}'
```

### 4.3 发布流程

```bash
# 1. 查看下一个待发布内容
curl http://localhost:8000/api/publish/next

# 2. 手动发布
curl -X POST http://localhost:8000/api/publish/ \
  -H "Content-Type: application/json" \
  -d '{"content_id": 1}'

# 3. 查看发布日志
curl http://localhost:8000/api/publish/logs
```

---

## 5. 定时任务

系统自动执行以下定时任务：

### 5.1 每日发布任务
- **时间**: 每天 08:00
- **任务**: 自动发布一条已审核通过的内容到微博
- **Celery任务**: `app.tasks.publish_tasks.daily_publish_task`

### 5.2 内容池检查任务
- **时间**: 每天 09:00
- **任务**: 检查内容池状态，低于阈值时发出警告
- **Celery任务**: `app.tasks.content_tasks.check_content_pool_task`

---

## 6. 错误处理

所有API错误响应格式：

```json
{
  "success": false,
  "message": "错误描述",
  "detail": "详细错误信息（仅开发环境）"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `422`: 数据验证失败
- `500`: 服务器内部错误

---

## 7. 开发调试

### 7.1 查看API文档

访问 `http://localhost:8000/docs` 可以：
- 查看所有API接口
- 在线测试API
- 查看请求/响应模型

### 7.2 健康检查

```bash
curl http://localhost:8000/health
```

### 7.3 查看日志

```bash
# Docker部署
docker-compose logs -f backend

# Systemd部署
tail -f logs/app_*.log
```

---

## 8. Python客户端示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 生成内容池
response = requests.post(f"{BASE_URL}/api/content/generate", json={"count": 30})
print(response.json())

# 处理内容
content_id = 1
response = requests.post(f"{BASE_URL}/api/content/{content_id}/process")
print(response.json())

# 审核通过
response = requests.post(
    f"{BASE_URL}/api/review/{content_id}/review",
    json={"approved": True, "reviewer_id": 1}
)
print(response.json())

# 发布到微博
response = requests.post(
    f"{BASE_URL}/api/publish/",
    json={"content_id": content_id}
)
print(response.json())
```
