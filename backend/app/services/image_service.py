import os
import time
from pathlib import Path
from typing import Optional
import httpx
from PIL import Image
from loguru import logger
from app.core.config import settings


class ImageService:
    def __init__(self):
        # OUTPUT_DIR_PATH 现在是可选的（直接返回 URL 时不需要）
        try:
            self.output_dir = Path(settings.OUTPUT_DIR_PATH)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create output directory: {e}. Will return URLs directly.")
            self.output_dir = None

    async def generate_image_dalle(self, prompt: str, filename: str) -> Optional[str]:
        """使用DALL-E生成图片（支持自定义API基础URL和模型）"""
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not configured")
            return None

        try:
            from openai import OpenAI

            # 创建客户端，支持自定义 base_url
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE if settings.OPENAI_API_BASE else None,
                timeout=120.0  # 增加超时时间到 120 秒
            )

            if settings.OPENAI_API_BASE:
                logger.info(f"Using custom API base: {settings.OPENAI_API_BASE}")

            model = settings.OPENAI_IMAGE_MODEL
            size = f"{settings.IMAGE_WIDTH}x{settings.IMAGE_HEIGHT}"
            logger.info(f"Using image model: {model}, size: {size}")
            logger.info(f"Prompt: {prompt[:100]}...")

            # 新版 OpenAI API (v1.x)
            logger.info("Calling images.generate API...")
            response = client.images.generate(
                model=model,
                prompt=prompt,
                n=1,
                size=size,
                quality="high",  # 添加画质参数
                response_format="url"  # 明确指定返回 URL
            )

            logger.info(f"API response received: {response}")

            # 尝试获取图片 URL
            if hasattr(response, 'data') and len(response.data) > 0:
                image_url = response.data[0].url
                logger.info(f"Generated image URL: {image_url}")
                return image_url
            else:
                logger.error(f"Unexpected response format: {response}")
                return None

        except Exception as e:
            logger.error(f"Failed to generate image with DALL-E: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def generate_image_stability(self, prompt: str, filename: str) -> Optional[str]:
        """使用Stability AI生成图片"""
        if not settings.STABILITY_API_KEY:
            logger.error("STABILITY_API_KEY not configured")
            return None

        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": settings.IMAGE_HEIGHT,
                "width": settings.IMAGE_WIDTH,
                "samples": 1,
                "steps": 30,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                image_data = data['artifacts'][0]['base64']

                import base64
                image_bytes = base64.b64decode(image_data)

                output_path = self.output_dir / filename
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)

                logger.info(f"Generated image saved to {output_path}")
                return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate image with Stability AI: {e}")
            return None

    async def generate_image(self, text: str, content_id: int) -> Optional[str]:
        """生成图片（自动选择可用的API）"""
        prompt = self._create_prompt(text)
        filename = f"content_{content_id}_{int(time.time())}.png"

        if settings.OPENAI_API_KEY:
            return await self.generate_image_dalle(prompt, filename)
        elif settings.STABILITY_API_KEY:
            return await self.generate_image_stability(prompt, filename)
        else:
            logger.error("No AI image generation API configured")
            return None

    def _create_prompt(self, text: str) -> str:
        """根据文案创建图片生成提示词"""
        base_prompt = (
            f"Create a beautiful, inspirational background image for this motivational quote: '{text}'. "
            f"The image should be aesthetic, calming, and suitable for social media. "
            f"Style: minimalist, modern, with soft colors and natural elements. "
            f"No text in the image."
        )
        return base_prompt

    def get_image_path(self, content_id: int) -> Optional[Path]:
        """获取内容对应的图片路径"""
        pattern = f"content_{content_id}_*.png"
        matches = list(self.output_dir.glob(pattern))
        return matches[0] if matches else None
