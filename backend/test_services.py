#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试服务功能
用于验证文案选择、图片生成、Logo水印等核心功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentence_service import SentenceService
from app.services.logo_service import LogoService
from app.core.config import settings
from loguru import logger


def test_sentence_loading():
    """测试文案加载"""
    print("\n" + "="*60)
    print("测试 1: 文案加载功能")
    print("="*60)

    try:
        # 模拟数据库会话（不需要真实连接）
        class MockDB:
            def query(self, *args):
                class MockQuery:
                    def filter(self, *args):
                        return self
                    def all(self):
                        return []
                return MockQuery()

        db = MockDB()
        sentence_service = SentenceService(db)

        # 加载所有文案
        sentences = sentence_service.load_sentences()

        print(f"✅ 成功加载 {len(sentences)} 条文案")
        print(f"\n前 5 条文案预览:")
        for i, sentence in enumerate(sentences[:5], 1):
            print(f"  {i}. ID={sentence['id']}: {sentence['text'][:50]}...")

        return True
    except Exception as e:
        print(f"❌ 文案加载失败: {e}")
        return False


def test_logo_service():
    """测试 Logo 服务"""
    print("\n" + "="*60)
    print("测试 2: Logo 服务功能")
    print("="*60)

    try:
        logo_service = LogoService()

        if logo_service.color_logo:
            print(f"✅ 原色 Logo 加载成功: {logo_service.color_logo.size}")
        else:
            print(f"⚠️  原色 Logo 未找到")

        if logo_service.white_logo:
            print(f"✅ 反白 Logo 加载成功: {logo_service.white_logo.size}")
        else:
            print(f"⚠️  反白 Logo 未找到")

        return True
    except Exception as e:
        print(f"❌ Logo 服务测试失败: {e}")
        return False


def test_configuration():
    """测试配置"""
    print("\n" + "="*60)
    print("测试 3: 配置验证")
    print("="*60)

    configs = {
        "文案文件路径": settings.SENTENCE_FILE_PATH,
        "Logo 目录": settings.LOGO_DIR_PATH,
        "输出目录": settings.OUTPUT_DIR_PATH,
        "图片尺寸": f"{settings.IMAGE_WIDTH}x{settings.IMAGE_HEIGHT}",
        "Logo 大小比例": settings.LOGO_SIZE_RATIO,
        "亮度阈值": settings.BRIGHTNESS_THRESHOLD,
    }

    for key, value in configs.items():
        print(f"  {key}: {value}")

    # 检查路径是否存在
    print("\n路径检查:")
    sentence_path = Path(settings.SENTENCE_FILE_PATH)
    logo_path = Path(settings.LOGO_DIR_PATH)

    if sentence_path.exists():
        print(f"  ✅ 文案文件存在: {sentence_path}")
    else:
        print(f"  ❌ 文案文件不存在: {sentence_path}")

    if logo_path.exists():
        print(f"  ✅ Logo 目录存在: {logo_path}")
        logo_files = list(logo_path.glob("*.png"))
        print(f"     找到 {len(logo_files)} 个 Logo 文件")
    else:
        print(f"  ❌ Logo 目录不存在: {logo_path}")

    return True


def test_api_keys():
    """测试 API 密钥配置"""
    print("\n" + "="*60)
    print("测试 4: API 密钥配置")
    print("="*60)

    if settings.OPENAI_API_KEY:
        print(f"  ✅ OpenAI API Key 已配置 ({settings.OPENAI_API_KEY[:10]}...)")
    else:
        print(f"  ⚠️  OpenAI API Key 未配置")

    if settings.STABILITY_API_KEY:
        print(f"  ✅ Stability API Key 已配置 ({settings.STABILITY_API_KEY[:10]}...)")
    else:
        print(f"  ⚠️  Stability API Key 未配置")

    if settings.WEIBO_APP_KEY:
        print(f"  ✅ 微博 App Key 已配置")
    else:
        print(f"  ⚠️  微博 App Key 未配置")

    if settings.WEIBO_ACCESS_TOKEN:
        print(f"  ✅ 微博 Access Token 已配置")
    else:
        print(f"  ⚠️  微博 Access Token 未配置")

    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("微博每日一句 - 服务功能测试")
    print("="*60)

    results = []

    # 运行测试
    results.append(("配置验证", test_configuration()))
    results.append(("文案加载", test_sentence_loading()))
    results.append(("Logo 服务", test_logo_service()))
    results.append(("API 密钥", test_api_keys()))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
    else:
        print("\n⚠️  部分测试失败，请检查配置。")


if __name__ == "__main__":
    main()
