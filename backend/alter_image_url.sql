-- 修改 image_url 字段类型为 TEXT 以支持长 URL
ALTER TABLE content MODIFY COLUMN image_url TEXT COMMENT '图片URL';
