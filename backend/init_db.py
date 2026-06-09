#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
执行: python init_database.py
"""

import pymysql
import sys

# 数据库连接信息
DB_CONFIG = {
    'host': '47.84.57.156',
    'port': 31910,
    'user': 'root',
    'password': 'N81P265Ru7ODZkp0VQz943GMibgExJqK',
    'database': 'zeabur',
    'charset': 'utf8mb4'
}

SQL_STATEMENTS = [
    # 创建 content 表
    """
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='内容表'
    """,

    # 创建 publish_log 表
    """
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='发布日志表'
    """
]

def main():
    print("=" * 60)
    print("微博每日一句 - 数据库初始化")
    print("=" * 60)
    print(f"连接到: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print()

    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("✅ 数据库连接成功")

        # 执行建表语句
        for i, sql in enumerate(SQL_STATEMENTS, 1):
            print(f"\n执行 SQL {i}/{len(SQL_STATEMENTS)}...")
            cursor.execute(sql)
            print(f"✅ 完成")

        connection.commit()

        # 验证表创建
        print("\n" + "=" * 60)
        print("验证表结构")
        print("=" * 60)

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n数据库中的表: {[t[0] for t in tables]}")

        for table in ['content', 'publish_log']:
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            print(f"\n【{table}】表结构:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")

        # 统计数据
        print("\n" + "=" * 60)
        print("数据统计")
        print("=" * 60)

        cursor.execute("SELECT COUNT(*) FROM content")
        content_count = cursor.fetchone()[0]
        print(f"content 表记录数: {content_count}")

        cursor.execute("SELECT COUNT(*) FROM publish_log")
        log_count = cursor.fetchone()[0]
        print(f"publish_log 表记录数: {log_count}")

        print("\n" + "=" * 60)
        print("🎉 数据库初始化完成！")
        print("=" * 60)

        cursor.close()
        connection.close()

        return 0

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
