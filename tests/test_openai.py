import os

import pytest
from dotenv import load_dotenv
from openai import OpenAI


@pytest.mark.integration
def test_openai():
    """Проверка подключения к OpenAI API"""
    load_dotenv(dotenv_path=".env")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    resp = client.models.list()
    assert len(resp.data) > 0
    print("✅ OpenAI работает, доступно моделей:", len(resp.data))
    print("Пример первой модели:", resp.data[0].id)


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_openai()
