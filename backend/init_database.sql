-- 微博每日一句 - 数据库初始化脚本
-- Database: zeabur @ Zeabur MySQL
-- 执行: mysqlsh --sql --host=47.84.57.156 --port=31910 --user=root --password=N81P265Ru7ODZkp0VQz943GMibgExJqK --schema=zeabur < init_database.sql

USE zeabur;

-- 删除已存在的表（如果需要重新初始化）
-- DROP TABLE IF EXISTS publish_log;
-- DROP TABLE IF EXISTS content;

-- 1. 创建 content 表
CREATE TABLE IF NOT EXISTS content (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sentence_id INT NOT NULL COMMENT '文案库序号(1-150)',
    text TEXT NOT NULL COMMENT '文案内容',
    image_url VARCHAR(255) COMMENT '图片URL',
    logo_version VARCHAR(20) COMMENT 'logo版本(原色/反白)',
    status ENUM('待审核', '已通过', '已拒绝', '已发布') DEFAULT '待审核' NOT NULL COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    reviewed_at DATETIME COMMENT '审核时间',
    published_at DATETIME COMMENT '发布时间',
    reviewer_id INT COMMENT '审核人ID',
    reject_reason TEXT COMMENT '拒绝原因',
    INDEX idx_status (status),
    INDEX idx_sentence_id (sentence_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='内容表';

-- 2. 创建 publish_log 表
CREATE TABLE IF NOT EXISTS publish_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content_id INT NOT NULL COMMENT '内容ID',
    weibo_id VARCHAR(50) COMMENT '微博ID',
    status ENUM('成功', '失败') NOT NULL COMMENT '发布状态',
    error_msg TEXT COMMENT '错误信息',
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    INDEX idx_content_id (content_id),
    INDEX idx_published_at (published_at),
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='发布日志表';

-- 3. 验证表创建
SHOW TABLES;

-- 4. 查看表结构
DESCRIBE content;
DESCRIBE publish_log;

-- 5. 插入测试数据（可选）
-- INSERT INTO content (sentence_id, text, status) VALUES
--     (1, '新的一天，不是重复昨天，而是改写故事的新一页。早安。', '待审核'),
--     (2, '把"我不行"换成"我再试试"，你会发现世界悄悄让了路。', '待审核'),
--     (3, '心里有光，哪怕走在最暗的路上，也不会害怕。早安。', '已通过');

SELECT '数据库初始化完成！' AS status;
SELECT COUNT(*) AS content_count FROM content;
SELECT COUNT(*) AS log_count FROM publish_log;
