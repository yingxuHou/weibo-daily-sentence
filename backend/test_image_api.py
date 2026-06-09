#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试云雾 AI 图片生成 API
"""

from openai import OpenAI

API_KEY = "sk-3HgTG9CBU040e4TVamdA2RkOAfB5wbT0mMisHrsGSZO3f7Ng"
API_BASE = "https://yunwu.ai/v1"
MODEL = "gpt-image-2"

def test_image_generation():
    print("=" * 60)
    print("Testing Image Generation API")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print(f"Model: {MODEL}")
    print()

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )

        prompt = "Create a beautiful, inspirational background image for this motivational quote: '每一次日出，都是生活重新开始的邀请函。'. The image should be aesthetic, calming, and suitable for social media. Style: minimalist, modern, with soft colors and natural elements. No text in the image."

        print("Sending request to generate image...")
        print(f"Prompt: {prompt[:100]}...")
        print()

        response = client.images.generate(
            model=MODEL,
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        print("[SUCCESS] Image generated!")
        print(f"Image URL: {response.data[0].url}")
        print()

        return 0

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(test_image_generation())
