import os
import pytest
from digests.ai_summary import generate_summary


@pytest.mark.integration
def test_generate_summary_smoke():
    """Интеграционный тест: генерация саммари через OpenAI"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    data = [
        {
            "title": "Биткоин растет",
            "content": "Цена BTC достигла 70,000$",
            "source": "crypto",
        },
        {
            "title": "Инфляция в США снижается",
            "content": "Последние данные показали замедление инфляции",
            "source": "economy",
        },
    ]

    summary = generate_summary(data, max_tokens=100)

    assert isinstance(summary, str)
    assert len(summary) > 10

    print("✅ Саммари успешно сгенерирован:", summary[:80], "...")
