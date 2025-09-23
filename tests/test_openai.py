# tests/test_openai.py

import os
import pytest
from openai import OpenAI
from dotenv import load_dotenv

@pytest.mark.integration
def test_openai():
    """Интеграционный тест: проверка подключения к OpenAI API"""

    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        pytest.skip("❌ Нет ключа OPENAI_API_KEY в .env")

    client = OpenAI(api_key=api_key)

    resp = client.models.list()

    # Проверяем, что список моделей не пустой
    assert isinstance(resp.data, list) and len(resp.data) > 0

    print("✅ OpenAI работает, доступно моделей:", len(resp.data))
    print("Пример первой модели:", resp.data[0].id)


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_openai()