import random
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.models.content import Content, ContentStatus
from loguru import logger


class SentenceService:
    def __init__(self, db: Session):
        self.db = db
        self.sentence_file = Path(settings.SENTENCE_FILE_PATH)

    def load_sentences(self) -> List[dict]:
        """从sentence.md加载所有文案"""
        if not self.sentence_file.exists():
            logger.error(f"Sentence file not found: {self.sentence_file}")
            raise FileNotFoundError(f"Sentence file not found: {self.sentence_file}")

        logger.info(f"Loading sentences from: {self.sentence_file.absolute()}")

        sentences = []
        sentence_id = 1
        line_count = 0
        empty_lines = 0

        with open(self.sentence_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                line = line.strip()
                # 跳过空行
                if line:
                    sentences.append({
                        'id': sentence_id,
                        'text': line
                    })
                    sentence_id += 1
                else:
                    empty_lines += 1

        logger.info(f"Loaded {len(sentences)} sentences from {self.sentence_file} (total lines: {line_count}, empty: {empty_lines})")
        return sentences

    def get_used_sentence_ids(self, days: int = 30) -> set:
        """获取最近N天已使用的文案ID"""
        cutoff_date = datetime.now() - timedelta(days=days)
        used_ids = self.db.query(Content.sentence_id).filter(
            Content.created_at >= cutoff_date
        ).all()
        return {id[0] for id in used_ids}

    def select_random_sentences(self, count: int = 30, dedup_days: int = 30) -> List[dict]:
        """随机选择N条未使用的文案"""
        all_sentences = self.load_sentences()
        used_ids = self.get_used_sentence_ids(dedup_days)

        available_sentences = [s for s in all_sentences if s['id'] not in used_ids]

        if len(available_sentences) < count:
            logger.warning(
                f"Not enough unused sentences. Available: {len(available_sentences)}, "
                f"Requested: {count}. Will reuse some sentences."
            )
            available_sentences = all_sentences

        selected = random.sample(available_sentences, min(count, len(available_sentences)))
        logger.info(f"Selected {len(selected)} sentences")
        return selected

    def create_content_batch(self, sentences: List[dict]) -> List[Content]:
        """批量创建内容记录"""
        contents = []
        for sentence in sentences:
            content = Content(
                sentence_id=sentence['id'],
                text=sentence['text'],
                status='待审核'  # 直接使用字符串字面量
            )
            self.db.add(content)
            contents.append(content)

        self.db.commit()
        logger.info(f"Created {len(contents)} content records")
        return contents

    def generate_content_pool(self, count: int = 30, auto_generate_images: bool = False) -> List[Content]:
        """生成内容池（选择文案并创建记录，可选自动生成图片）"""
        sentences = self.select_random_sentences(count)
        contents = self.create_content_batch(sentences)

        # 如果启用自动生成图片
        if auto_generate_images:
            logger.info(f"Auto-generating images for {len(contents)} contents...")
            from app.services.image_service import ImageService
            image_service = ImageService()

            for content in contents:
                try:
                    logger.info(f"Generating image for content {content.id}...")
                    import asyncio
                    image_url = asyncio.run(image_service.generate_image(content.text, content.id))

                    if image_url:
                        content.image_url = image_url
                        logger.info(f"Image generated for content {content.id}: {image_url}")
                    else:
                        logger.warning(f"Failed to generate image for content {content.id}")
                except Exception as e:
                    logger.error(f"Error generating image for content {content.id}: {e}")
                    # 继续处理下一个，不中断整个流程

            self.db.commit()
            logger.info(f"Image generation completed for {len(contents)} contents")

        return contents

    def get_content_pool_status(self) -> dict:
        """获取内容池状态"""
        pending_count = self.db.query(func.count(Content.id)).filter(
            Content.status == ContentStatus.PENDING
        ).scalar()

        approved_count = self.db.query(func.count(Content.id)).filter(
            Content.status == ContentStatus.APPROVED
        ).scalar()

        return {
            'pending': pending_count,
            'approved': approved_count,
            'total': pending_count + approved_count,
            'warning': approved_count < settings.CONTENT_POOL_WARNING_THRESHOLD
        }
