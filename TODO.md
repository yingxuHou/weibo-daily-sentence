# 微博每日一句鸡汤运营AI员工 - 任务清单

## 项目概述
基于现有150条文案库，通过AI配图+Logo水印，实现微博每日自动发布。

---

## Phase 1：MVP版本（2周）

### 1. 搭建项目基础架构
**状态**：待开始  
**描述**：搭建Python后端 + 数据库  
**技术栈**：
- 后端框架：待定
- 数据库：MySQL/PostgreSQL
- 依赖管理：pip/poetry

**交付物**：
- [ ] 项目目录结构
- [ ] 虚拟环境配置
- [ ] 依赖包安装
- [ ] 基础配置文件

---

### 2. 实现文案选择模块
**状态**：待开始  
**描述**：从sentence.md读取并选择30条文案  
**功能要点**：
- 读取 `D:\university\Pudow\onesentence-oneday\sentence.md`
- 支持顺序/随机选择策略
- 记录已使用文案ID

**交付物**：
- [ ] 文案读取函数
- [ ] 选择策略实现（顺序/随机）
- [ ] 已使用文案记录功能

---

### 3. 集成AI图片生成API
**状态**：待开始  
**描述**：集成Stable Diffusion/DALL-E/Midjourney API  
**功能要点**：
- 根据文案内容生成配图
- 图片尺寸：1080x1080
- 图片风格：清新/温暖/治愈

**技术选型**：
- Stable Diffusion API
- DALL-E 3 API
- Midjourney API（通过第三方）

**交付物**：
- [ ] API密钥配置
- [ ] 图片生成函数
- [ ] 提示词模板优化
- [ ] 错误处理和重试机制

---

### 4. 开发Logo水印添加功能
**状态**：待开始  
**描述**：使用Pillow库在图片上添加企业Logo  
**功能要点**：
- 智能检测背景亮度
- 自动选择原色/反白Logo
- 固定位置和比例

**技术实现**：
```python
from PIL import Image
import numpy as np

def add_logo_watermark(bg_path, output_path):
    bg = Image.open(bg_path).convert("RGB")
    
    # 检测右下角区域亮度
    region = bg.crop((bg.width-200, bg.height-200, bg.width, bg.height))
    brightness = np.array(region).mean()
    
    # 选择logo版本
    if brightness > 128:
        logo_path = "logo/PUDOW朴道健康水专家-原色.png"
    else:
        logo_path = "logo/PUDOW朴道健康水专家-反白.png"
    
    logo = Image.open(logo_path).convert("RGBA")
    logo_width = int(bg.width * 0.13)
    logo = logo.resize((logo_width, int(logo.height * logo_width / logo.width)))
    
    position = (bg.width - logo_width - 20, bg.height - logo.height - 20)
    bg.paste(logo, position, logo)
    bg.save(output_path, quality=95)
    
    return "原色" if brightness > 128 else "反白"
```

**交付物**：
- [ ] Logo水印添加函数
- [ ] 亮度检测算法
- [ ] Logo版本自动选择
- [ ] 批量处理功能

---

### 5. 设计并实现数据库表结构
**状态**：待开始  
**描述**：创建content表和publish_log表  

**表结构**：

#### content表
```sql
CREATE TABLE content (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sentence_id INT NOT NULL COMMENT '文案库序号(1-150)',
    text TEXT NOT NULL COMMENT '文案内容',
    image_url VARCHAR(255) COMMENT '图片URL',
    logo_version VARCHAR(20) COMMENT 'logo版本(原色/反白)',
    status ENUM('待审核', '已通过', '已拒绝', '已发布') DEFAULT '待审核',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    published_at DATETIME,
    reviewer_id INT,
    reject_reason TEXT,
    INDEX idx_status (status),
    INDEX idx_sentence_id (sentence_id)
);
```

#### publish_log表
```sql
CREATE TABLE publish_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content_id INT NOT NULL,
    weibo_id VARCHAR(50),
    status ENUM('成功', '失败') NOT NULL,
    error_msg TEXT,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content(id)
);
```

**交付物**：
- [ ] 数据库设计文档
- [ ] SQL建表脚本
- [ ] ORM模型定义
- [ ] 数据库迁移脚本

---

### 6. 开发审核管理后台界面
**状态**：待开始  
**描述**：展示30组内容，支持编辑/删除/批量操作  

**功能需求**：
- 展示文案+配图列表
- 单条编辑/删除/替换
- 批量通过/拒绝
- 标记问题内容
- 重新生成图片

**页面设计**：
- 列表页：卡片式展示，每张卡片显示文案+配图
- 详情页：大图预览，文案编辑
- 操作按钮：通过、拒绝、重新生成、删除

**交付物**：
- [ ] 前端页面（HTML/CSS/JS）
- [ ] 后端API接口
- [ ] 审核流程逻辑
- [ ] 权限控制

---

### 7. 集成微博API
**状态**：待开始  
**描述**：实现OAuth认证和内容发布  

**功能要点**：
- OAuth 2.0认证
- 图片上传接口
- 内容发布接口
- API限流控制

**微博API接口**：
- 发布接口：`/statuses/share`
- 图片上传：`/statuses/upload`
- 账号认证：OAuth 2.0

**交付物**：
- [ ] 微博开放平台账号申请
- [ ] OAuth认证流程
- [ ] 图片上传功能
- [ ] 内容发布功能
- [ ] API调用频率控制

---

### 8. 实现定时发布功能
**状态**：待开始  
**描述**：每天早上8点自动发布一条内容  

**技术方案**：
- Cron定时任务
- Celery异步任务
- APScheduler调度器

**功能要点**：
- 定时触发（每天8:00）
- 从内容池取出一条
- 调用微博API发布
- 记录发布结果
- 失败自动重试（最多3次）

**交付物**：
- [ ] 定时任务配置
- [ ] 发布逻辑实现
- [ ] 失败重试机制
- [ ] 发布结果通知

---

## Phase 2：完善版本（2周）

### 9. 开发内容池预警机制
**状态**：待开始  
**描述**：剩余<5条时自动通知  

**功能要点**：
- 实时监控内容池数量
- 低于阈值时发送通知
- 自动触发内容生成

**交付物**：
- [ ] 内容池监控功能
- [ ] 预警通知（邮件/短信/企业微信）
- [ ] 自动补充机制

---

### 10. 实现30天去重机制
**状态**：待开始  
**描述**：避免短期内重复文案  

**功能要点**：
- 记录每条文案的使用时间
- 选择文案时过滤30天内已使用的
- 当可用文案不足时提前预警

**交付物**：
- [ ] 使用记录表设计
- [ ] 去重算法实现
- [ ] 循环使用策略

---

### 11. 添加敏感词过滤功能
**状态**：待开始  
**描述**：过滤敏感内容，降低风险  

**功能要点**：
- 敏感词库维护
- 文案自动检测
- 图片内容审核（可选）

**交付物**：
- [ ] 敏感词库文件
- [ ] 过滤算法实现
- [ ] 审核前自动检测

---

### 12. 开发发布监控和日志记录功能
**状态**：待开始  
**描述**：完整的操作日志和监控  

**功能要点**：
- 发布成功/失败日志
- 系统操作日志
- 错误告警
- 数据统计看板

**交付物**：
- [ ] 日志记录系统
- [ ] 监控告警配置
- [ ] 数据统计报表

---

## Phase 3：测试与部署

### 13. 测试完整流程
**状态**：待开始  
**描述**：端到端测试  

**测试内容**：
- 文案选择功能
- 图片生成功能
- Logo水印添加
- 审核流程
- 定时发布
- 异常处理

**交付物**：
- [ ] 测试用例文档
- [ ] 功能测试报告
- [ ] Bug修复记录

---

### 14. 部署到生产环境
**状态**：待开始  
**描述**：配置服务器和定时任务  

**部署清单**：
- [ ] 服务器环境配置
- [ ] 数据库部署
- [ ] 代码部署
- [ ] 定时任务配置
- [ ] 域名和SSL证书
- [ ] 监控告警配置
- [ ] 备份策略

---

## 资源清单

### 现有资源
- **文案库**：`D:\university\Pudow\onesentence-oneday\sentence.md`（150条）
- **Logo资源**：`D:\university\Pudow\onesentence-oneday\logo\`
  - PUDOW朴道健康水专家-原色.png
  - PUDOW朴道健康水专家-反白.png
  - PUDOW朴道健康水专家-墨稿.png

### 需要申请的资源
- [ ] 微博开放平台账号
- [ ] AI图片生成API密钥（Stable Diffusion/DALL-E）
- [ ] 服务器（云服务器或本地）
- [ ] 域名（如需要Web管理后台）

---

## 进度跟踪

| 任务 | 状态 | 开始时间 | 完成时间 | 负责人 | 备注 |
|------|------|----------|----------|--------|------|
| 1. 项目基础架构 | 待开始 | - | - | - | - |
| 2. 文案选择模块 | 待开始 | - | - | - | - |
| 3. AI图片生成 | 待开始 | - | - | - | - |
| 4. Logo水印添加 | 待开始 | - | - | - | - |
| 5. 数据库设计 | 待开始 | - | - | - | - |
| 6. 审核后台 | 待开始 | - | - | - | - |
| 7. 微博API集成 | 待开始 | - | - | - | - |
| 8. 定时发布 | 待开始 | - | - | - | - |
| 9. 内容池预警 | 待开始 | - | - | - | - |
| 10. 去重机制 | 待开始 | - | - | - | - |
| 11. 敏感词过滤 | 待开始 | - | - | - | - |
| 12. 监控日志 | 待开始 | - | - | - | - |
| 13. 完整测试 | 待开始 | - | - | - | - |
| 14. 生产部署 | 待开始 | - | - | - | - |

---

## 里程碑

- **Week 1-2**：完成任务1-4（核心功能）
- **Week 3-4**：完成任务5-8（MVP版本上线）
- **Week 5-6**：完成任务9-12（功能完善）
- **Week 7**：完成任务13-14（测试部署）

---

## 注意事项

1. **优先级**：任务1-8是MVP版本，必须优先完成
2. **依赖关系**：任务1必须先完成，任务2-4可并行开发
3. **风险控制**：人工审核不可跳过，确保内容质量
4. **成本控制**：AI图片生成API按量计费，注意成本
5. **合规性**：确保内容符合微博平台规范
