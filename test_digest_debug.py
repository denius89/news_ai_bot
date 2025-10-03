#!/usr/bin/env python3
"""
Debug script to test digest functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.digest_service import build_daily_digest


def test_digest():
    print("Testing build_daily_digest...")

    try:
        digest_text, news_items = build_daily_digest(limit=5)
        print(f"✅ Success!")
        print(f"Digest text: {digest_text[:100]}...")
        print(f"News items count: {len(news_items)}")
        print(f"News items type: {type(news_items)}")

        if news_items:
            print(f"First item type: {type(news_items[0])}")
            if hasattr(news_items[0], 'model_dump'):
                print("✅ First item has model_dump method")
            else:
                print("❌ First item does not have model_dump method")

            print(f"First item attributes: {dir(news_items[0])}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_digest()
