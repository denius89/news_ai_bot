"""
Unit tests for Notifications API endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.webapp import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_auth():
    """Mock authentication for tests."""
    with patch("src.webapp.verify_telegram_auth") as mock_auth:
        mock_auth.return_value = {
            "success": True,
            "user_id": 123456789,
            "telegram_id": 123456789,
            "method": "test",
            "message": "Authenticated",
        }
        yield mock_auth


class TestNotificationsAPI:
    """Test notifications API endpoints."""

    def test_get_notifications_missing_user_id(self, client, mock_auth):
        """Test GET /api/notifications without user_id parameter."""
        response = client.get("/api/notifications")
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "user_id parameter is required" in data["message"]

    @patch("routes.api_routes.list_notifications")
    def test_get_notifications_success(self, mock_get_notifications, client, mock_auth):
        """Test successful GET /api/notifications."""
        # Mock database response
        mock_get_notifications.return_value = [
            {
                "id": "notif-1",
                "title": "Test Notification",
                "message": "Test message",
                "category": "crypto",
                "read": False,
                "created_at": "2025-10-02T10:00:00Z",
            },
            {
                "id": "notif-2",
                "title": "Read Notification",
                "message": "Already read",
                "category": "economy",
                "read": True,
                "created_at": "2025-10-01T10:00:00Z",
            },
        ]

        response = client.get("/api/notifications?user_id=test-user-123")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "notifications" in data["data"]
        assert data["data"]["total_count"] == 2
        assert data["data"]["unread_count"] == 1

    @patch("routes.api_routes.list_notifications")
    def test_get_notifications_empty(self, mock_get_notifications, client, mock_auth):
        """Test GET /api/notifications with no notifications."""
        mock_get_notifications.return_value = []

        response = client.get("/api/notifications?user_id=test-user-123")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["data"]["notifications"] == []
        assert data["data"]["total_count"] == 0
        assert data["data"]["unread_count"] == 0

    @patch("routes.api_routes.list_notifications")
    def test_get_notifications_error(self, mock_get_notifications, client, mock_auth):
        """Test GET /api/notifications with database error."""
        mock_get_notifications.side_effect = Exception("Database error")

        response = client.get("/api/notifications?user_id=test-user-123")
        # API should return success with empty data on error (graceful degradation)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["data"]["notifications"] == []

    def test_mark_notification_read_not_implemented(self, client, mock_auth):
        """Test marking notification as read (not implemented yet)."""
        response = client.post(
            "/api/notifications/mark-read",
            json={"user_id": "test-user-123", "notification_id": "notif-1"},
        )
        assert response.status_code == 501
        data = response.get_json()
        assert data["status"] == "error"
        assert "Use /api/user_notifications/mark_read instead" in data["message"]

    def test_get_notification_settings_not_implemented(self, client, mock_auth):
        """Test getting notification settings (not implemented yet)."""
        response = client.get("/api/notification-settings?user_id=test-user-123")
        assert response.status_code == 501
        data = response.get_json()
        assert data["status"] == "error"
        assert "Not implemented yet" in data["message"]

    def test_update_notification_settings_not_implemented(self, client, mock_auth):
        """Test updating notification settings (not implemented yet)."""
        response = client.post(
            "/api/notification-settings/update",
            json={"user_id": "test-user-123", "category": "crypto", "enabled": True},
        )
        assert response.status_code == 501
        data = response.get_json()
        assert data["status"] == "error"
        assert "Not implemented yet" in data["message"]
