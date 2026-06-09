from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np
from loguru import logger
from app.core.config import settings


class LogoService:
    def __init__(self):
        self.logo_dir = Path(settings.LOGO_DIR_PATH)
        self.color_logo = None
        self.white_logo = None
        self._load_logos()

    def _load_logos(self):
        """加载Logo文件"""
        color_path = self.logo_dir / "PUDOW朴道健康水专家-原色.png"
        white_path = self.logo_dir / "PUDOW朴道健康水专家-反白.png"

        if color_path.exists():
            self.color_logo = Image.open(color_path).convert("RGBA")
            logger.info(f"Loaded color logo from {color_path}")
        else:
            logger.warning(f"Color logo not found: {color_path}")

        if white_path.exists():
            self.white_logo = Image.open(white_path).convert("RGBA")
            logger.info(f"Loaded white logo from {white_path}")
        else:
            logger.warning(f"White logo not found: {white_path}")

    def calculate_brightness(self, image: Image.Image, region: Tuple[int, int, int, int]) -> float:
        """计算图片指定区域的亮度"""
        cropped = image.crop(region)
        grayscale = cropped.convert('L')
        pixels = np.array(grayscale)
        avg_brightness = np.mean(pixels)
        return avg_brightness

    def select_logo_version(self, image: Image.Image, position: str = "bottom_right") -> Tuple[Image.Image, str]:
        """根据背景亮度选择Logo版本"""
        width, height = image.size
        logo_width = int(width * settings.LOGO_SIZE_RATIO)
        logo_height = int(height * settings.LOGO_SIZE_RATIO)
        margin = settings.LOGO_MARGIN

        if position == "bottom_right":
            region = (
                width - logo_width - margin,
                height - logo_height - margin,
                width - margin,
                height - margin
            )
        elif position == "bottom_left":
            region = (
                margin,
                height - logo_height - margin,
                margin + logo_width,
                height - margin
            )
        elif position == "top_right":
            region = (
                width - logo_width - margin,
                margin,
                width - margin,
                margin + logo_height
            )
        else:  # top_left
            region = (
                margin,
                margin,
                margin + logo_width,
                margin + logo_height
            )

        brightness = self.calculate_brightness(image, region)
        logger.info(f"Background brightness at {position}: {brightness:.2f}")

        if brightness > settings.BRIGHTNESS_THRESHOLD:
            logo = self.color_logo
            version = "color"
        else:
            logo = self.white_logo
            version = "white"

        if logo is None:
            logger.error(f"Selected logo version '{version}' not available")
            logo = self.color_logo or self.white_logo
            version = "color" if self.color_logo else "white"

        return logo, version

    def add_watermark(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        position: str = "bottom_right"
    ) -> Tuple[str, str]:
        """添加Logo水印"""
        if not self.color_logo and not self.white_logo:
            logger.error("No logo files available")
            raise FileNotFoundError("No logo files found in logo directory")

        base_image = Image.open(image_path).convert("RGBA")
        logo, version = self.select_logo_version(base_image, position)

        width, height = base_image.size
        logo_width = int(width * settings.LOGO_SIZE_RATIO)
        logo_height = int(height * settings.LOGO_SIZE_RATIO)

        logo_resized = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        margin = settings.LOGO_MARGIN
        if position == "bottom_right":
            pos = (width - logo_width - margin, height - logo_height - margin)
        elif position == "bottom_left":
            pos = (margin, height - logo_height - margin)
        elif position == "top_right":
            pos = (width - logo_width - margin, margin)
        else:  # top_left
            pos = (margin, margin)

        base_image.paste(logo_resized, pos, logo_resized)

        if output_path is None:
            output_path = image_path.replace('.png', '_watermarked.png')

        base_image = base_image.convert("RGB")
        base_image.save(output_path, "PNG", quality=95)

        logger.info(f"Added {version} logo watermark to {output_path}")
        return output_path, version

    def process_content_image(self, image_path: str) -> Tuple[str, str]:
        """处理内容图片（添加水印）"""
        output_path = image_path.replace('.png', '_final.png')
        return self.add_watermark(image_path, output_path)
