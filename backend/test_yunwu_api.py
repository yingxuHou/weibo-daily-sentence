#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试云雾 AI 图片生成 API - 使用 requests 调试
"""

import requests
import json

API_KEY = "sk-3HgTG9CBU040e4TVamdA2RkOAfB5wbT0mMisHrsGSZO3f7Ng"
API_BASE = "https://yunwu.ai/v1"
MODEL = "gpt-image-2"

def test_with_requests():
    """使用 requests 库测试，查看详细响应"""
    print("=" * 60)
    print("Testing with requests library")
    print("=" * 60)

    url = f"{API_BASE}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "prompt": "A beautiful sunset over mountains",
        "n": 1,
        "size": "1024x1024"
    }

    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        print("Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        print(f"Response Body:")
        print(response.text)

        if response.status_code == 200:
            data = response.json()
            print()
            print("[SUCCESS]")
            print(f"Image URL: {data.get('data', [{}])[0].get('url', 'N/A')}")

        return 0

    except requests.Timeout:
        print("[ERROR] Request timed out")
        return 1
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(test_with_requests())
