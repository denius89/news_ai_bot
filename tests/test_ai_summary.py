import os
import pytest

from digests.ai_summary import generate_summary, generate_summary_why_important


@pytest.mark.integration
def test_generate_summary_smoke():
    """Интеграционный тест: генерация обычного саммари через OpenAI"""

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

    print("✅ Обычное саммари успешно сгенерировано:", summary[:80], "...")


@pytest.mark.integration
def test_generate_summary_why_important_smoke():
    """Интеграционный тест: генерация саммари в стиле 'почему важно'"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    item = {
        "title": "ФРС сохранила ставку",
        "content": (
            "Федеральная резервная система США сохранила процентную ставку без изменений, "
            "но намекнула на возможное снижение в следующем квартале."
        ),
        "source": "economy",
    }

    summary = generate_summary_why_important(item, max_tokens=120)

    assert isinstance(summary, str)
    assert "Почему важно" in summary  # проверяем наличие блока
    assert "—" in summary  # должны быть буллеты

    print("✅ Саммари 'почему важно' успешно сгенерировано:", summary[:80], "...")
