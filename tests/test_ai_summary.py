import os
import pytest

from digests.ai_summary import (
    generate_summary_why_important_json,
    generate_summary_why_important,
    generate_batch_summary,
)

# ✅ все тесты в этом файле — интеграционные
pytestmark = pytest.mark.integration


def test_generate_summary_why_important_json_smoke():
    """Интеграционный тест: JSON-аннотация новости"""

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

    result = generate_summary_why_important_json(item, max_tokens=120)

    assert isinstance(result, dict)
    assert "summary" in result
    assert "why_important" in result
    assert isinstance(result["why_important"], list)

    print("✅ JSON-аннотация успешно сгенерирована:", result)


def test_generate_summary_why_important_smoke():
    """Интеграционный тест: текстовый блок для Telegram"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    item = {
        "title": "Биткоин растет",
        "content": "Цена BTC достигла 70,000$",
        "source": "crypto",
    }

    text = generate_summary_why_important(item, max_tokens=120)

    assert isinstance(text, str)
    assert "Почему это важно" in text

    print("✅ Текстовый блок 'почему важно' успешно сгенерирован:", text[:120], "...")


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
