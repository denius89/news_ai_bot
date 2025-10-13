"""
Tests for BaseEventProvider.

Tests the abstract base class functionality.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from events.providers.base_provider import BaseEventProvider


class TestProvider(BaseEventProvider):
    """Test implementation of BaseEventProvider."""

    async def fetch_events(self, start_date: datetime, end_date: datetime):
        """Mock implementation."""
        return [
            {
                "title": "Test Event",
                "starts_at": start_date,
                "subcategory": "test",
                "importance": 0.8,
                "description": "Test description",
                "link": "https://example.com",
                "location": "Test Location",
                "organizer": "Test Organizer",
                "metadata": {"test": True},
            }
        ]


class TestBaseEventProvider:
    """Test cases for BaseEventProvider."""

    def test_init(self):
        """Test provider initialization."""
        provider = TestProvider()
        assert provider.name == "test"
        assert provider.category == "test"
        assert provider.session is None

    def test_create_unique_hash(self):
        """Test unique hash creation."""
        provider = TestProvider()
        title = "Test Event"
        starts_at = datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc)
        source = "test_source"

        hash1 = provider.create_unique_hash(title, starts_at, source)
        hash2 = provider.create_unique_hash(title, starts_at, source)
        hash3 = provider.create_unique_hash("Different Event", starts_at, source)

        # Same inputs should produce same hash
        assert hash1 == hash2
        # Different inputs should produce different hash
        assert hash1 != hash3
        # Hash should be 64 characters (SHA256)
        assert len(hash1) == 64

    def test_normalize_event(self):
        """Test event normalization."""
        provider = TestProvider()

        event_data = {
            "title": "  Test Event  ",
            "subcategory": "crypto",
            "starts_at": datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc),
            "ends_at": datetime(2025, 1, 15, 14, 0, tzinfo=timezone.utc),
            "importance": 0.8,
            "description": "Test description",
            "link": "https://example.com",
            "location": "Test Location",
            "organizer": "Test Organizer",
            "metadata": {"test": True},
        }

        normalized = provider.normalize_event(event_data)

        assert normalized["title"] == "Test Event"  # Trimmed
        assert normalized["category"] == "test"  # From provider
        assert normalized["subcategory"] == "crypto"
        assert normalized["starts_at"] == event_data["starts_at"]
        assert normalized["ends_at"] == event_data["ends_at"]
        assert normalized["source"] == "test"
        assert normalized["importance"] == 0.8
        assert normalized["description"] == "Test description"
        assert normalized["location"] == "Test Location"
        assert normalized["organizer"] == "Test Organizer"
        assert normalized["metadata"] == {"test": True}
        assert normalized["status"] == "upcoming"
        assert "unique_hash" in normalized

    def test_normalize_event_missing_fields(self):
        """Test event normalization with missing fields."""
        provider = TestProvider()

        event_data = {
            "title": "Test Event",
            "starts_at": datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc),
        }

        normalized = provider.normalize_event(event_data)

        assert normalized["title"] == "Test Event"
        assert normalized["category"] == "test"
        assert normalized["subcategory"] == "general"  # Default
        assert normalized["importance"] == 0.5  # Default
        assert normalized["description"] is None
        assert normalized["link"] == ""  # Default
        assert normalized["location"] is None
        assert normalized["organizer"] is None
        assert normalized["metadata"] == {}  # Default
        assert normalized["status"] == "upcoming"

    def test_normalize_event_invalid(self):
        """Test event normalization with invalid data."""
        provider = TestProvider()

        # Missing title
        event_data = {
            "starts_at": datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc),
        }

        normalized = provider.normalize_event(event_data)
        assert normalized is None

    def test_get_info(self):
        """Test provider info."""
        provider = TestProvider()

        info = provider.get_info()

        assert info["name"] == "test"
        assert info["category"] == "test"
        assert "description" in info

    @pytest.mark.asyncio
    async def test_close(self):
        """Test provider close."""
        provider = TestProvider()
        provider.session = Mock()

        await provider.close()

        assert provider.session is None

    @pytest.mark.asyncio
    async def test_close_no_session(self):
        """Test provider close without session."""
        provider = TestProvider()

        # Should not raise exception
        await provider.close()

        assert provider.session is None
