# 微博自动发布方案

## 结论

项目应通过微博开放平台 OAuth2 和官方 API 发布，不建议用 Selenium、扫码登录、
Cookie 注入或模拟网页点击。这些方案容易受登录风控和页面改版影响，也会扩大账号凭据
泄露风险。

本项目现在采用三层结构：

- `backend/app/publishers/weibo.py`：OAuth2、图片读取、微博 API 请求和错误解析。
- `backend/app/services/publication_service.py`：内容状态校验、并发锁、发布日志和状态更新。
- `backend/app/tasks/publish_tasks.py`：Celery Beat 每日调度和有限重试。

手动 API 与定时任务共用同一个发布编排服务，避免两套逻辑产生不同状态。

## 官方接口

实现使用以下微博开放平台接口：

- OAuth 授权：`https://api.weibo.com/oauth2/authorize`
- 换取令牌：`https://api.weibo.com/oauth2/access_token`
- 纯文字微博：`POST /2/statuses/update.json`
- 图片微博：`POST /2/statuses/upload.json`

参考入口：

- [微博开放平台](https://open.weibo.com/)
- [OAuth2 authorize](https://open.weibo.com/wiki/Oauth2/authorize)
- [OAuth2 access_token](https://open.weibo.com/wiki/Oauth2/access_token)
- [statuses/upload](https://open.weibo.com/wiki/2/statuses/upload)
- [statuses/update](https://open.weibo.com/wiki/2/statuses/update)

微博开放平台的可用接口和调用额度取决于应用类型、审核状态及账号授权。上线前必须在
应用控制台确认当前应用拥有内容发布权限；仅创建应用并拿到 App Key，不代表一定可以
调用发布接口。

## 配置步骤

1. 在微博开放平台创建应用，配置与 `WEIBO_REDIRECT_URI` 完全一致的回调地址。
2. 启动后端，访问 `GET /api/publish/weibo/authorize-url`。
3. 用目标微博账号打开返回的授权地址并授权，记录回调 URL 中的 `code`。
4. 服务端向 OAuth `access_token` 接口提交 `code`，将返回令牌写入部署环境的
   `WEIBO_ACCESS_TOKEN`。令牌不得提交到 Git。
5. 访问 `GET /api/publish/weibo/config`，确认 `credentials_configured=true`。
6. 先通过 `POST /api/publish/` 对一条已审核内容做人工测试。
7. 测试通过后设置 `WEIBO_PUBLISH_ENABLED=True`，再启动 Celery Worker 和 Beat。

主要环境变量：

```dotenv
WEIBO_APP_KEY=...
WEIBO_APP_SECRET=...
WEIBO_REDIRECT_URI=https://your-domain.example/weibo/callback
WEIBO_ACCESS_TOKEN=...
WEIBO_PUBLISH_ENABLED=False
WEIBO_REQUEST_TIMEOUT_SECONDS=20
WEIBO_MAX_IMAGE_SIZE_MB=20
DAILY_PUBLISH_TIME=08:00
```

## 自动发布行为

- Celery Beat 按 `DAILY_PUBLISH_TIME`（`Asia/Shanghai`）触发。
- 只选择最早审核通过且未发布的内容。
- 发布时对内容行加数据库锁，降低手动发布与定时发布撞车的概率。
- 图片支持本地文件路径和 `http/https` URL；远程内容必须返回 `image/*`。
- 成功后写入微博 ID，并将内容状态改为“已发布”。
- 失败后记录微博错误信息；仅对微博明确返回的限流或服务端错误做有限重试。
- 网络断开等结果不确定的 POST 不自动重试，避免微博实际已发布却再次创建重复内容。

## 上线检查

- 确认发布接口权限和调用频率，不以开发环境结果代替生产应用审核。
- 确认 Access Token 有效期，建立到期提醒和重新授权流程。
- 保持 `WEIBO_PUBLISH_ENABLED=False`，直到手动发布验证成功。
- Worker 与 Beat 只能各有预期数量，尤其避免启动多个 Beat。
- 对发布失败日志和待发布内容池数量配置告警。
- 定期在微博端抽查图片、文字、重复内容和账号风控提示。
