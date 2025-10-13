"""
Тесты для Digest Generator v2.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from models.news import NewsItem
from digests.generator import generate_digest, _convert_v2_to_text


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_with_v2_params():
    """Test digest generation with v2 parameters"""

    # Mock news items
    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    # Mock fetch_recent_news
    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        # Mock v2 generation
        with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
            mock_v2.return_value = {
                "title": "Test Digest",
                "dek": "Test dek",
                "summary": "Test summary",
                "why_important": ["Important point 1", "Important point 2"],
                "meta": {
                    "style_profile": "analytical",
                    "tone": "insightful",
                    "length": "medium",
                    "audience": "general",
                    "confidence": 0.9,
                },
            }

            result = await generate_digest(
                limit=10,
                category="tech",
                ai=True,
                style="analytical",
                tone="insightful",
                length="medium",
                audience="general",
                use_v2=True,
            )

            assert isinstance(result, str)
            assert "Test Digest" in result
            assert "Test summary" in result
            assert "Important point 1" in result

            # Verify v2 was called with correct parameters
            mock_v2.assert_called_once()
            call_args = mock_v2.call_args[1]
            assert call_args["category"] == "tech"
            assert call_args["style_profile"] == "analytical"
            assert call_args["tone"] == "insightful"
            assert call_args["length"] == "medium"
            assert call_args["audience"] == "general"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_v2_fallback_to_legacy():
    """Test fallback to legacy when v2 fails"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        # Mock v2 failure
        with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
            mock_v2.return_value = {"error": "V2 generation failed"}

            # Mock legacy service
            with patch("digests.generator.DigestAIService") as mock_service:
                mock_instance = MagicMock()
                mock_instance.build_digest.return_value = "Legacy digest result"
                mock_service.return_value = mock_instance

                result = await generate_digest(limit=10, category="tech", ai=True, style="analytical", use_v2=True)

                assert isinstance(result, str)
                assert "Legacy digest result" in result

                # Verify legacy service was called
                mock_instance.build_digest.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_legacy_mode():
    """Test legacy mode when use_v2=False"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        # Mock legacy service
        with patch("digests.generator.DigestAIService") as mock_service:
            mock_instance = MagicMock()
            mock_instance.build_digest.return_value = "Legacy digest result"
            mock_service.return_value = mock_instance

            result = await generate_digest(limit=10, category="tech", ai=True, style="analytical", use_v2=False)

            assert isinstance(result, str)
            assert "Legacy digest result" in result

            # Verify legacy service was called
            mock_instance.build_digest.assert_called_once()


@pytest.mark.unit
def test_convert_v2_to_text():
    """Test conversion of v2 result to text format"""

    v2_result = {
        "title": "Test Digest",
        "dek": "Test dek",
        "summary": "Test summary content",
        "why_important": ["Important point 1", "Important point 2"],
        "context": "Test context",
        "what_next": "Test what next",
        "sources_cited": ["Source 1", "Source 2"],
    }

    result = _convert_v2_to_text(v2_result)

    assert isinstance(result, str)
    assert "<b>Test Digest</b>" in result
    assert "<i>Test dek</i>" in result
    assert "Test summary content" in result
    assert "<b>Почему это важно:</b>" in result
    assert "— Important point 1" in result
    assert "— Important point 2" in result
    assert "<b>Контекст:</b> Test context" in result
    assert "<b>Что дальше:</b> Test what next" in result
    assert "<b>Источники:</b> Source 1, Source 2" in result


@pytest.mark.unit
def test_convert_v2_to_text_minimal():
    """Test conversion with minimal v2 result"""

    v2_result = {"title": "Minimal Digest", "summary": "Minimal summary"}

    result = _convert_v2_to_text(v2_result)

    assert isinstance(result, str)
    assert "<b>Minimal Digest</b>" in result
    assert "Minimal summary" in result


@pytest.mark.unit
def test_convert_v2_to_text_empty():
    """Test conversion with empty v2 result"""

    result = _convert_v2_to_text({})

    assert isinstance(result, str)
    assert "<b>Дайджест новостей</b>" in result


@pytest.mark.unit
def test_convert_v2_to_text_none():
    """Test conversion with None v2 result"""

    result = _convert_v2_to_text(None)

    assert isinstance(result, str)
    assert "Ошибка конвертации v2 результата" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_all_style_profiles():
    """Test all style profiles"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    styles = ["analytical", "business", "meme", "newsroom", "magazine", "casual"]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        for style in styles:
            with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
                mock_v2.return_value = {
                    "title": f"Test {style} Digest",
                    "summary": f"Test {style} summary",
                    "why_important": ["Important point"],
                    "meta": {"style_profile": style},
                }

                result = await generate_digest(limit=10, category="tech", ai=True, style=style, use_v2=True)

                assert isinstance(result, str)
                assert f"Test {style} Digest" in result

                # Verify correct style was passed
                call_args = mock_v2.call_args[1]
                assert call_args["style_profile"] == style


@pytest.mark.asyncio
@pytest.mark.unit
async def test_all_tones():
    """Test all tone options"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    tones = ["neutral", "insightful", "critical", "optimistic"]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        for tone in tones:
            with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
                mock_v2.return_value = {
                    "title": f"Test {tone} Digest",
                    "summary": f"Test {tone} summary",
                    "why_important": ["Important point"],
                    "meta": {"tone": tone},
                }

                result = await generate_digest(
                    limit=10, category="tech", ai=True, style="analytical", tone=tone, use_v2=True
                )

                assert isinstance(result, str)
                assert f"Test {tone} Digest" in result

                # Verify correct tone was passed
                call_args = mock_v2.call_args[1]
                assert call_args["tone"] == tone


@pytest.mark.asyncio
@pytest.mark.unit
async def test_all_lengths():
    """Test all length options"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    lengths = ["short", "medium", "long"]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        for length in lengths:
            with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
                mock_v2.return_value = {
                    "title": f"Test {length} Digest",
                    "summary": f"Test {length} summary",
                    "why_important": ["Important point"],
                    "meta": {"length": length},
                }

                result = await generate_digest(
                    limit=10, category="tech", ai=True, style="analytical", length=length, use_v2=True
                )

                assert isinstance(result, str)
                assert f"Test {length} Digest" in result

                # Verify correct length was passed
                call_args = mock_v2.call_args[1]
                assert call_args["length"] == length


@pytest.mark.asyncio
@pytest.mark.unit
async def test_all_audiences():
    """Test all audience options"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    audiences = ["general", "pro"]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        for audience in audiences:
            with patch("digests.generator.generate_summary_journalistic_v2") as mock_v2:
                mock_v2.return_value = {
                    "title": f"Test {audience} Digest",
                    "summary": f"Test {audience} summary",
                    "why_important": ["Important point"],
                    "meta": {"audience": audience},
                }

                result = await generate_digest(
                    limit=10, category="tech", ai=True, style="analytical", audience=audience, use_v2=True
                )

                assert isinstance(result, str)
                assert f"Test {audience} Digest" in result

                # Verify correct audience was passed
                call_args = mock_v2.call_args[1]
                assert call_args["audience"] == audience


@pytest.mark.asyncio
@pytest.mark.unit
async def test_no_ai_mode():
    """Test non-AI mode (fallback digest)"""

    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="tech",
            credibility=0.8,
            importance=0.7,
        )
    ]

    with patch("digests.generator.fetch_recent_news", return_value=news_items):
        # Mock DigestAIService
        with patch("digests.generator.DigestAIService") as mock_service:
            mock_instance = MagicMock()
            mock_instance._build_fallback_digest.return_value = "Fallback digest result"
            mock_service.return_value = mock_instance

            result = await generate_digest(limit=10, category="tech", ai=False, style="analytical")  # No AI

            assert isinstance(result, str)
            assert "Fallback digest result" in result

            # Verify fallback was called
            mock_instance._build_fallback_digest.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_empty_news_list():
    """Test handling of empty news list"""

    with patch("digests.generator.fetch_recent_news", return_value=[]):
        result = await generate_digest(limit=10, category="tech", ai=True, style="analytical")

        assert isinstance(result, str)
        assert "новостей нет" in result
