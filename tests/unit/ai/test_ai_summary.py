import os
import pytest
from unittest.mock import Mock, patch

from digests.ai_summary import (
    generate_summary_why_important_json,
    generate_summary_why_important,
    generate_batch_summary,
    generate_summary_journalistic_v2,
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
    with patch("digests.ai_summary.get_client") as mock_get_client:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"title": "Тестовая новость", "why_important": ["Важно для тестирования", "Проверяет структуру"]}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

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
    with patch("digests.ai_summary.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

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
    with patch("digests.ai_summary.get_client") as mock_get_client:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"title": "Bitcoin Price Surge", "why_important": ["Market impact", "Investment implications"]}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

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
    with patch("digests.ai_summary.get_client") as mock_get_client:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content="📰 Дайджест новостей:\n\n1. News 1\n2. News 2\n\n<b>Почему это важно:</b>\n1. Важно для рынка\n2. Влияет на инвестиции"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_batch_summary(data, max_tokens=300, style="analytical")

        assert isinstance(result, str)
        assert "Дайджест новостей" in result or "News 1" in result
        assert "Почему это важно" in result
        assert len(result) > 50


def test_generate_summary_with_empty_data():
    """Unit test: обработка пустых данных"""
    empty_data = []

    with patch("digests.ai_summary.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Empty data error")
        mock_get_client.return_value = mock_client

        # Должен вернуть fallback даже для пустых данных
        result = generate_batch_summary(empty_data, max_tokens=100)

        assert isinstance(result, str)
        assert len(result) > 0  # Должен быть какой-то fallback текст


# ============================================================================
# V2 JOURNALISTIC SYSTEM TESTS
# ============================================================================


def test_generate_summary_v2_tech_analytical():
    """Test v2 generation for tech/analytical style"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    # Mock news items
    news_items = [
        {
            "title": "OpenAI представила GPT-5",
            "content": "Новая модель показывает улучшенные возможности рассуждения",
            "importance": 0.8,
            "credibility": 0.9,
            "source": "TechCrunch",
            "published_at": "2024-01-15T10:00:00Z",
        }
    ]

    result = generate_summary_journalistic_v2(
        news_items=news_items,
        category="tech",
        style_profile="analytical",
        tone="insightful",
        length="medium",
        audience="general",
    )

    assert isinstance(result, dict)
    assert "title" in result
    assert "summary" in result
    assert "why_important" in result
    assert "meta" in result

    print("✅ V2 tech/analytical digest generated:", result["title"])


def test_generate_summary_v2_crypto_newsroom():
    """Test v2 generation for crypto/newsroom style"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    news_items = [
        {
            "title": "Bitcoin достиг $50,000",
            "content": "Криптовалюта впервые с апреля превысила психологический барьер",
            "importance": 0.9,
            "credibility": 0.8,
            "source": "CoinDesk",
            "published_at": "2024-01-15T12:00:00Z",
        }
    ]

    result = generate_summary_journalistic_v2(
        news_items=news_items,
        category="crypto",
        style_profile="newsroom",
        tone="neutral",
        length="short",
        audience="pro",
    )

    assert isinstance(result, dict)
    assert result["meta"]["style_profile"] == "newsroom"
    assert result["meta"]["tone"] == "neutral"
    assert result["meta"]["length"] == "short"

    print("✅ V2 crypto/newsroom digest generated:", result["title"])


def test_validate_sources_low_importance():
    """Test that low importance sources are skipped"""

    news_items = [
        {
            "title": "Low importance news",
            "content": "This news has low importance",
            "importance": 0.3,  # Below threshold
            "credibility": 0.9,
            "source": "Test",
            "published_at": "2024-01-15T10:00:00Z",
        }
    ]

    result = generate_summary_journalistic_v2(
        news_items=news_items, category="tech", style_profile="analytical", min_importance=0.6, min_credibility=0.7
    )

    assert "skipped_reason" in result
    assert "low importance" in result["skipped_reason"]

    print("✅ Low importance sources correctly skipped")


def test_output_schema_validation():
    """Test that output matches v2 schema"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    news_items = [
        {
            "title": "Test news",
            "content": "Test content",
            "importance": 0.8,
            "credibility": 0.9,
            "source": "Test",
            "published_at": "2024-01-15T10:00:00Z",
        }
    ]

    result = generate_summary_journalistic_v2(
        news_items=news_items,
        category="tech",
        style_profile="magazine",
        tone="optimistic",
        length="long",
        audience="general",
    )

    # Check required fields
    required_fields = ["title", "dek", "summary", "why_important", "meta"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"

    # Check meta structure
    meta = result["meta"]
    meta_fields = ["style_profile", "tone", "length", "audience", "confidence"]
    for field in meta_fields:
        assert field in meta, f"Missing meta field: {field}"

    # Check confidence range
    assert 0.0 <= meta["confidence"] <= 1.0

    print("✅ V2 schema validation passed")


def test_fallback_to_v1():
    """Test fallback when v2 is not available"""

    # Mock the case where v2 prompts are not available
    with pytest.patch("digests.ai_summary.HAS_V2", False):
        news_items = [
            {
                "title": "Test news",
                "content": "Test content",
                "importance": 0.8,
                "credibility": 0.9,
                "source": "Test",
                "published_at": "2024-01-15T10:00:00Z",
            }
        ]

        result = generate_summary_journalistic_v2(news_items=news_items, category="tech", style_profile="analytical")

        assert "fallback" in result
        assert result["fallback"] is True
        assert "legacy_result" in result

        print("✅ V2 fallback to v1 working correctly")


def test_all_style_profiles():
    """Test all 4 style profiles"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    news_items = [
        {
            "title": "Test news",
            "content": "Test content",
            "importance": 0.8,
            "credibility": 0.9,
            "source": "Test",
            "published_at": "2024-01-15T10:00:00Z",
        }
    ]

    styles = ["newsroom", "analytical", "magazine", "casual"]

    for style in styles:
        result = generate_summary_journalistic_v2(
            news_items=news_items, category="tech", style_profile=style, tone="neutral", length="medium"
        )

        assert isinstance(result, dict)
        if "meta" in result:
            assert result["meta"]["style_profile"] == style

        print(f"✅ Style {style} working correctly")


def test_all_tones():
    """Test all tone options"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("❌ Нет OPENAI_API_KEY в .env")

    news_items = [
        {
            "title": "Test news",
            "content": "Test content",
            "importance": 0.8,
            "credibility": 0.9,
            "source": "Test",
            "published_at": "2024-01-15T10:00:00Z",
        }
    ]

    tones = ["neutral", "insightful", "critical", "optimistic"]

    for tone in tones:
        result = generate_summary_journalistic_v2(
            news_items=news_items, category="tech", style_profile="analytical", tone=tone, length="medium"
        )

        assert isinstance(result, dict)
        if "meta" in result:
            assert result["meta"]["tone"] == tone

        print(f"✅ Tone {tone} working correctly")
