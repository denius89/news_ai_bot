"""
Unit tests for Events API endpoints.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone

from webapp import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestEventsAPI:
    """Test cases for Events API endpoints."""

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_success(self, mock_get_events, client):
        """Test successful GET /api/events."""
        from models.event import EventItem
        
        mock_events = [
            EventItem(
                event_id="event-1",
                title="Bitcoin Conference 2025",
                event_time=datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc),
                category="crypto",
                importance=0.8,
                description="Major crypto conference"
            ),
            EventItem(
                event_id="event-2",
                title="Fed Meeting",
                event_time=datetime(2025, 12, 15, 14, 0, 0, tzinfo=timezone.utc),
                category="economy",
                importance=0.9,
                description="Federal Reserve meeting"
            )
        ]
        mock_get_events.return_value = mock_events

        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'events' in data['data']
        assert len(data['data']['events']) == 2
        assert data['data']['total_count'] == 2

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_with_limit_offset(self, mock_get_events, client):
        """Test GET /api/events with limit and offset parameters."""
        from models.event import EventItem
        
        mock_events = [
            EventItem(
                event_id=f"event-{i}",
                title=f"Event {i}",
                event_time=datetime(2025, 12, 1 + i, 10, 0, 0, tzinfo=timezone.utc),
                category="crypto",
                importance=0.7,
                description=f"Test event {i}"
            )
            for i in range(1, 6)
        ]
        mock_get_events.return_value = mock_events

        response = client.get('/api/events?limit=3&offset=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['events']) == 5  # Mock returns all, limit handled by DB

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_empty_database(self, mock_get_events, client):
        """Test GET /api/events with empty database."""
        mock_get_events.return_value = []

        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['events'] == []
        assert data['data']['total_count'] == 0

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_database_error(self, mock_get_events, client):
        """Test GET /api/events with database error."""
        mock_get_events.side_effect = Exception("Database error")

        response = client.get('/api/events')
        assert response.status_code == 200  # API should return success with empty data
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['events'] == []

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_with_category_filter(self, mock_get_events, client):
        """Test GET /api/events with category filter."""
        from models.event import EventItem
        
        mock_events = [
            EventItem(
                event_id="crypto-event-1",
                title="Crypto Event",
                event_time=datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc),
                category="crypto",
                importance=0.8,
                description="Crypto related event"
            )
        ]
        mock_get_events.return_value = mock_events

        response = client.get('/api/events?category=crypto')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['events']) == 1
        assert data['data']['events'][0]['category'] == 'crypto'

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_with_multiple_categories(self, mock_get_events, client):
        """Test GET /api/events with multiple categories filter."""
        from models.event import EventItem
        
        mock_events = [
            EventItem(
                event_id="multi-event-1",
                title="Multi Category Event",
                event_time=datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc),
                category="crypto",
                importance=0.8,
                description="Event in multiple categories"
            ),
            EventItem(
                event_id="multi-event-2",
                title="Another Multi Event",
                event_time=datetime(2025, 12, 2, 10, 0, 0, tzinfo=timezone.utc),
                category="economy",
                importance=0.9,
                description="Another multi-category event"
            )
        ]
        mock_get_events.return_value = mock_events

        response = client.get('/api/events?categories=crypto&categories=economy')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['events']) == 2

    @patch('routes.api_routes.get_upcoming_events')
    def test_get_events_verify_structure(self, mock_get_events, client):
        """Test that GET /api/events returns properly structured event data."""
        from models.event import EventItem
        
        mock_events = [
            EventItem(
                event_id="structure-test-1",
                title="Structure Test Event",
                event_time=datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc),
                category="technology",
                importance=0.7,
                description="Test event for structure verification"
            )
        ]
        mock_get_events.return_value = mock_events

        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        
        # Verify event structure
        event = data['data']['events'][0]
        required_fields = ['id', 'title', 'event_time', 'category', 'importance', 'description']
        for field in required_fields:
            assert field in event, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(event['title'], str)
        assert isinstance(event['category'], str)
        assert isinstance(event['importance'], (int, float))
        assert event['importance'] >= 0 and event['importance'] <= 1
