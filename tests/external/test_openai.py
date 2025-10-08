"""
Интеграционный тест для проверки подключения к OpenAI API.
"""

import os
import pytest
from dotenv import load_dotenv
from openai import OpenAI


@pytest.mark.integration
def test_openai_completion():
    """Проверка, что OpenAI API отвечает на простой запрос."""

    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        pytest.skip("❌ Пропущен: нет OPENAI_API_KEY в .env")

    client = OpenAI(api_key=key)

    # Минимальный тест — пробуем сгенерировать короткий текст
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5,
    )

    assert resp.choices
    assert isinstance(resp.choices[0].message.content, str)
