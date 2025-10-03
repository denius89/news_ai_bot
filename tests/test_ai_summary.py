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


def test_generate_summary_why_important_json_structure():
    """Unit test: проверка структуры JSON ответа"""
    item = {
        "title": "Тестовая новость",
        "content": "Тестовое содержание новости",
        "source": "test",
    }

    # Мокаем вызов OpenAI, чтобы тест работал без API ключа
    with pytest.Mock() as mock_openai:
        mock_openai.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"title": "Тестовая новость", "why_important": ["Важно для тестирования", "Проверяет структуру"]}'
                    }
                }
            ]
        }

        # Используем patch для мокирования
        with pytest.patch('digests.ai_summary.openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_openai.return_value

            result = generate_summary_why_important_json(item, max_tokens=120)

            assert isinstance(result, dict)
            assert "title" in result
            assert "why_important" in result
            assert isinstance(result["why_important"], list)
            assert len(result["why_important"]) > 0


def test_generate_summary_why_important_fallback():
    """Unit test: проверка fallback блока 'Почему это важно'"""
    item = {
        "title": "Тестовая новость",
        "content": "Тестовое содержание",
        "source": "test",
    }

    # Мокаем ошибку OpenAI для тестирования fallback
    with pytest.patch('digests.ai_summary.openai_client') as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        result = generate_summary_why_important(item, max_tokens=120)

        assert isinstance(result, str)
        assert "Почему это важно" in result
        assert "Тестовая новость" in result


def test_generate_summary_why_important_json_with_keys():
    """Unit test: проверка что JSON содержит правильные ключи"""
    item = {
        "title": "Bitcoin Price Surge",
        "content": "Bitcoin reached new all-time high",
        "source": "crypto",
    }

    expected_keys = {"title", "why_important"}

    # Мокаем успешный ответ OpenAI
    with pytest.patch('digests.ai_summary.openai_client') as mock_client:
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"title": "Bitcoin Price Surge", "why_important": ["Market impact", "Investment implications"]}'
                    }
                }
            ]
        }
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_summary_why_important_json(item, max_tokens=120)

        # Проверяем что все ожидаемые ключи присутствуют
        assert set(result.keys()) == expected_keys
        assert result["title"] == "Bitcoin Price Surge"
        assert isinstance(result["why_important"], list)
        assert len(result["why_important"]) == 2


def test_generate_batch_summary_structure():
    """Unit test: проверка структуры batch summary"""
    data = [
        {
            "title": "News 1",
            "content": "Content 1",
            "source": "test",
        },
        {
            "title": "News 2",
            "content": "Content 2",
            "source": "test",
        },
    ]

    # Мокаем успешный ответ
    with pytest.patch('digests.ai_summary.openai_client') as mock_client:
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "📰 Дайджест новостей:\n\n1. News 1\n2. News 2\n\n<b>Почему это важно:</b>\n1. Важно для рынка\n2. Влияет на инвестиции"
                    }
                }
            ]
        }
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_batch_summary(data, max_tokens=300, style="analytical")

        assert isinstance(result, str)
        assert "Дайджест новостей" in result or "News 1" in result
        assert "Почему это важно" in result
        assert len(result) > 50


def test_generate_summary_with_empty_data():
    """Unit test: обработка пустых данных"""
    empty_data = []

    with pytest.patch('digests.ai_summary.openai_client') as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("Empty data error")

        # Должен вернуть fallback даже для пустых данных
        result = generate_batch_summary(empty_data, max_tokens=100)

        assert isinstance(result, str)
        assert len(result) > 0  # Должен быть какой-то fallback текст
