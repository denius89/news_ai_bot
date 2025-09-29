import os
import pytest

from digests.ai_summary import generate_summary_why_important, generate_batch_summary


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

    assert isinstance(summary, dict)
    assert "summary" in summary
    assert "why_important" in summary
    assert isinstance(summary["why_important"], list)

    print("✅ Саммари 'почему важно' успешно сгенерировано:", summary)


@pytest.mark.integration
def test_generate_batch_summary_smoke():
    """Интеграционный тест: генерация цельного дайджеста"""

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

    summary = generate_batch_summary(data, max_tokens=300, style="analytical")

    assert isinstance(summary, str)
    assert len(summary) > 20
    assert "Почему это важно" in summary

    print("✅ Batch-дайджест успешно сгенерирован:", summary[:120], "...")
