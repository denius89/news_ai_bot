#!/usr/bin/env python3
"""
Test Flask digest route
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.news_routes import news_bp

app = Flask(__name__)
app.register_blueprint(news_bp)


def test_digest_route():
    print("Testing Flask digest route...")

    with app.test_client() as client:
        try:
            response = client.get('/digest')
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success!")
                content = response.get_data(as_text=True)
                print(f"Content length: {len(content)}")
                print(f"Content preview: {content[:200]}...")
            else:
                print(f"❌ Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_digest_route()
