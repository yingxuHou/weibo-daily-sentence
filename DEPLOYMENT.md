# Weibo Daily Sentence - 部署指南

## 部署方式

### 方式一：Docker部署（推荐）

#### 1. 准备环境

确保服务器已安装：
- Docker 20.10+
- Docker Compose 2.0+

#### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入生产环境配置
vim .env
```

必须配置的环境变量：
```bash
ENV=production
DATABASE_URL=mysql+pymysql://user:password@host:port/database?charset=utf8mb4
REDIS_URL=redis://redis:6379/0
WEIBO_APP_KEY=your_app_key
WEIBO_APP_SECRET=your_app_secret
WEIBO_ACCESS_TOKEN=your_access_token
OPENAI_API_KEY=your_openai_key  # 或 STABILITY_API_KEY
```

#### 3. 部署

```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh

# 或手动执行
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
```

#### 4. 查看状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# 查看API文档
# http://your-server-ip:8000/docs
```

#### 5. 停止服务

```bash
docker-compose down
```

---

### 方式二：Systemd服务部署

#### 1. 准备环境

```bash
# 安装Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 安装Redis
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# 安装MySQL客户端
sudo apt install libmysqlclient-dev
```

#### 2. 安装依赖

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
vim .env
```

#### 4. 运行数据库迁移

```bash
alembic upgrade head
```

#### 5. 配置Systemd服务

```bash
# 复制服务文件
sudo cp weibo-daily.service /etc/systemd/system/
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/

# 编辑服务文件，修改路径
sudo vim /etc/systemd/system/weibo-daily.service
sudo vim /etc/systemd/system/celery-worker.service
sudo vim /etc/systemd/system/celery-beat.service

# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start weibo-daily
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# 设置开机自启
sudo systemctl enable weibo-daily
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat

# 查看状态
sudo systemctl status weibo-daily
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

#### 6. 配置Nginx反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/onesentence-oneday/static;
    }

    location /data/images {
        alias /path/to/onesentence-oneday/data/images;
    }
}
```

---

## 生产环境检查清单

### 安全配置

- [ ] 修改 `.env` 中的敏感信息
- [ ] 限制CORS允许的域名（修改 `app/main.py` 中的 `allow_origins`）
- [ ] 配置防火墙规则
- [ ] 使用HTTPS（配置SSL证书）
- [ ] 设置数据库访问白名单

### 性能优化

- [ ] 配置Uvicorn workers数量（建议：CPU核心数 * 2 + 1）
- [ ] 配置数据库连接池大小
- [ ] 配置Redis持久化
- [ ] 设置日志轮转策略

### 监控告警

- [ ] 配置日志收集（如ELK、Loki）
- [ ] 配置应用监控（如Prometheus、Grafana）
- [ ] 配置错误告警（如Sentry）
- [ ] 配置内容池低库存告警

### 备份策略

- [ ] 配置数据库定期备份
- [ ] 配置生成图片定期备份
- [ ] 配置日志归档策略

---

## 常用运维命令

### Docker部署

```bash
# 重启服务
docker-compose restart backend

# 查看实时日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash

# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 手动触发定时任务
docker-compose exec backend python -c "from app.tasks.publish_tasks import daily_publish_task; daily_publish_task()"
```

### Systemd部署

```bash
# 重启服务
sudo systemctl restart weibo-daily

# 查看日志
sudo journalctl -u weibo-daily -f

# 查看Celery日志
tail -f logs/app_*.log
```

---

## 故障排查

### 1. 数据库连接失败

检查：
- 数据库服务是否运行
- DATABASE_URL配置是否正确
- 网络连接是否正常
- 数据库用户权限是否足够

### 2. Redis连接失败

检查：
- Redis服务是否运行：`redis-cli ping`
- REDIS_URL配置是否正确
- 防火墙是否阻止连接

### 3. 定时任务不执行

检查：
- Celery Beat服务是否运行
- Celery Worker服务是否运行
- 查看Celery日志：`docker-compose logs celery_beat`

### 4. 微博发布失败

检查：
- WEIBO_ACCESS_TOKEN是否有效
- 微博API配额是否用完
- 图片文件是否存在
- 查看发布日志：`/api/publish/logs`

### 5. AI图片生成失败

检查：
- OPENAI_API_KEY或STABILITY_API_KEY是否配置
- API密钥是否有效
- API配额是否用完
- 网络连接是否正常

---

## API文档

部署完成后访问：
- Swagger UI: `http://your-server-ip:8000/docs`
- ReDoc: `http://your-server-ip:8000/redoc`

---

## 技术支持

如遇问题，请查看：
1. 应用日志：`logs/app_*.log`
2. API文档：`/docs`
3. 健康检查：`/health`
