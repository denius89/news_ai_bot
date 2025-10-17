"""
Integration tests for events flow.

Tests the complete flow from fetching events to storing them.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock

from events.events_parser import EventsParser
from database.events_service import EventsService


class TestEventsFlow:
    """Test cases for complete events flow."""

    @pytest.mark.asyncio
    async def test_fetch_and_store_events_flow(self):
        """Test complete flow: fetch events -> AI filter -> store."""
        # Mock providers
        mock_provider = Mock()
        mock_provider.fetch_events = Mock(
            return_value=[
                {
                    "title": "High Importance Event",
                    "starts_at": datetime.now(timezone.utc) + timedelta(days=1),
                    "subcategory": "crypto",
                    "importance": 0.8,
                    "description": "Important crypto event",
                    "source": "test_provider",
                },
                {
                    "title": "Low Importance Event",
                    "starts_at": datetime.now(timezone.utc) + timedelta(days=1),
                    "subcategory": "general",
                    "importance": 0.4,
                    "description": "Less important event",
                    "source": "test_provider",
                },
            ]
        )
        mock_provider.normalize_event = Mock(
            side_effect=lambda x: {
                "title": x["title"],
                "category": "crypto",
                "subcategory": x["subcategory"],
                "starts_at": x["starts_at"],
                "importance": x["importance"],
                "description": x["description"],
                "source": x["source"],
                "unique_hash": "test_hash",
                "status": "upcoming",
            }
        )

        # Mock events parser - patch get_events_parser to return our mock
        with patch("tools.events.fetch_events.get_events_parser") as mock_get_parser:
            mock_parser = Mock()
            mock_parser.providers = {"test_provider": mock_provider}
            # Use AsyncMock for async method
            mock_parser.fetch_events = AsyncMock(
                return_value=[
                    Mock(
                        title="High Importance Event",
                        category="crypto",
                        subcategory="crypto",
                        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
                        importance=0.8,
                        importance_score=0.8,
                        description="Important crypto event",
                        source="test_provider",
                        __dict__={"importance_score": 0.8},
                    ),
                    Mock(
                        title="Low Importance Event",
                        category="crypto",
                        subcategory="general",
                        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
                        importance=0.4,
                        importance_score=0.4,
                        description="Less important event",
                        source="test_provider",
                        __dict__={"importance_score": 0.4},
                    ),
                ]
            )
            mock_get_parser.return_value = mock_parser

            # Mock ML evaluator to avoid loading model
            with patch("tools.events.fetch_events.evaluator_v2") as mock_evaluator:
                mock_evaluator.evaluate_importance = Mock(side_effect=lambda x: x.get("importance", 0.5))

                # Mock events service
                with patch("database.events_service.EventsService") as mock_service_class:
                    mock_service = Mock()
                    mock_service.insert_events = Mock(return_value=1)  # Only high importance event stored
                    mock_service_class.return_value = mock_service

                    # Import and test the function
                    from tools.events.fetch_events import fetch_and_store_events

                    result = await fetch_and_store_events(days_ahead=7, categories=["crypto"], dry_run=False)

                    # Verify results
                    assert result["success"] is True
                    assert result["events_fetched"] == 1  # Only high importance event
                    assert result["events_stored"] == 1
                    assert result["dry_run"] is False

                    # Verify AI filtering worked (importance >= 0.6)
                    mock_service.insert_events.assert_called_once()
                    stored_events = mock_service.insert_events.call_args[0][0]
                    assert len(stored_events) == 1
                    assert stored_events[0]["title"] == "High Importance Event"

    @pytest.mark.asyncio
    async def test_fetch_events_dry_run(self):
        """Test fetching events in dry run mode."""
        # Mock events parser - patch get_events_parser
        with patch("tools.events.fetch_events.get_events_parser") as mock_get_parser:
            mock_parser = Mock()
            # Use AsyncMock for async method
            mock_parser.fetch_events = AsyncMock(return_value=[])
            mock_get_parser.return_value = mock_parser

            # Mock ML evaluator
            with patch("tools.events.fetch_events.evaluator_v2") as mock_evaluator:
                mock_evaluator.evaluate_importance = Mock(return_value=0.5)

                # Import and test the function
                from tools.events.fetch_events import fetch_and_store_events

                result = await fetch_and_store_events(days_ahead=7, categories=["crypto"], dry_run=True)

                # Verify results
                assert result["success"] is True
                assert result["events_fetched"] == 0
                assert result["events_stored"] == 0
                assert result["dry_run"] is True

    @pytest.mark.asyncio
    async def test_update_event_results_flow(self):
        """Test updating event results."""
        # Mock events service - patch get_events_service
        with patch("tools.events.update_event_results.get_events_service") as mock_get_service:
            mock_service = Mock()
            # Use AsyncMock for async methods
            mock_service.get_completed_events_without_results = AsyncMock(
                return_value=[
                    {"id": 1, "title": "Completed Event", "status": "upcoming"},
                    {"id": 2, "title": "Another Event", "status": "upcoming"},
                ]
            )
            mock_service.update_event_status = AsyncMock(return_value=True)
            mock_get_service.return_value = mock_service

            # Import and test the function
            from tools.events.update_event_results import update_event_results

            result = await update_event_results(days_back=3, categories=["crypto"], dry_run=False)

            # Verify results
            assert result["success"] is True
            assert result["events_found"] == 2
            assert result["events_updated"] == 2
            assert result["dry_run"] is False

            # Verify service calls
            mock_service.get_completed_events_without_results.assert_called_once_with(3)
            assert mock_service.update_event_status.call_count == 2

    @pytest.mark.asyncio
    async def test_events_parser_dynamic_loading(self):
        """Test dynamic provider loading from configuration."""
        # Simply test that EventsParser can be instantiated
        # The actual provider loading is tested in unit tests
        parser = EventsParser()

        # Verify parser has providers dict
        assert hasattr(parser, "providers")
        assert isinstance(parser.providers, dict)
        # In real environment, providers should be loaded from config
        # But we don't need to test the full loading mechanism here

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in events flow."""
        # Mock parser that raises exception - patch get_events_parser
        with patch("tools.events.fetch_events.get_events_parser") as mock_get_parser:
            mock_parser = Mock()
            # Use AsyncMock that raises exception
            mock_parser.fetch_events = AsyncMock(side_effect=Exception("Network error"))
            mock_get_parser.return_value = mock_parser

            # Import and test the function
            from tools.events.fetch_events import fetch_and_store_events

            result = await fetch_and_store_events(days_ahead=7, dry_run=True)

            # Verify error handling
            assert result["success"] is False
            assert "error" in result
            assert "Network error" in result["error"]
