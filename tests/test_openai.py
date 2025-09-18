# tests/test_openai.py

import os
from openai import OpenAI
from dotenv import load_dotenv

def test_openai():
    """Проверка подключения к OpenAI API"""
    load_dotenv(dotenv_path=".env")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    resp = client.models.list()
    print("✅ OpenAI работает, доступно моделей:", len(resp.data))
    print("Пример первой модели:", resp.data[0].id)

if __name__ == "__main__":
    test_openai()