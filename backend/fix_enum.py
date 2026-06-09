#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据库 ENUM 类型
执行: python fix_enum.py
"""

import pymysql
import sys

DB_CONFIG = {
    'host': '47.84.57.156',
    'port': 31910,
    'user': 'root',
    'password': 'N81P265Ru7ODZkp0VQz943GMibgExJqK',
    'database': 'zeabur',
    'charset': 'utf8mb4'
}

def main():
    print('=' * 60)
    print('Fix Database ENUM Types')
    print('=' * 60)

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print('[OK] Connected to database')

        # Drop existing tables
        print('\n[1/3] Dropping existing tables...')
        cursor.execute('DROP TABLE IF EXISTS publish_log')
        cursor.execute('DROP TABLE IF EXISTS content')
        print('[OK] Tables dropped')

        # Create content table with English ENUM
        print('\n[2/3] Creating content table with English ENUM...')
        sql_content = '''
        CREATE TABLE content (
            id INT PRIMARY KEY AUTO_INCREMENT,
            sentence_id INT NOT NULL,
            text TEXT NOT NULL,
            image_url VARCHAR(255),
            logo_version VARCHAR(20),
            status ENUM('待审核', '已通过', '已拒绝', '已发布') DEFAULT '待审核' NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reviewed_at DATETIME,
            published_at DATETIME,
            reviewer_id INT,
            reject_reason TEXT,
            INDEX idx_status (status),
            INDEX idx_sentence_id (sentence_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
        cursor.execute(sql_content)
        print('[OK] Content table created')

        # Create publish_log table
        print('\n[3/3] Creating publish_log table...')
        sql_log = '''
        CREATE TABLE publish_log (
            id INT PRIMARY KEY AUTO_INCREMENT,
            content_id INT NOT NULL,
            weibo_id VARCHAR(50),
            status ENUM('成功', '失败') NOT NULL,
            error_msg TEXT,
            published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_content_id (content_id),
            FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
        cursor.execute(sql_log)
        print('[OK] Publish_log table created')

        conn.commit()

        # Verify
        print('\n' + '=' * 60)
        print('Verification')
        print('=' * 60)

        cursor.execute("SHOW CREATE TABLE content")
        result = cursor.fetchone()
        print(f'\nContent table definition:\n{result[1][:200]}...')

        print('\n' + '=' * 60)
        print('[SUCCESS] Database schema fixed!')
        print('=' * 60)

        cursor.close()
        conn.close()

        return 0

    except Exception as e:
        print(f'\n[ERROR] {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
