"""
Unit tests for Notifications API endpoints.
"""

import pytest

from webapp import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestNotificationsAPI:
    """Test notifications API endpoints."""

    def test_get_notifications_missing_user_id(self, client):
        """Test GET /api/notifications without user_id parameter."""
        response = client.get('/api/notifications')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'user_id parameter is required' in data['message']

    def test_get_notifications_success(self, client):
        """Test successful GET /api/notifications."""
        response = client.get('/api/notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'notifications' in data['data']
        assert data['data']['total_count'] == 0  # Demo returns empty notifications
        assert data['data']['unread_count'] == 0

    def test_get_notifications_empty(self, client):
        """Test GET /api/notifications with no notifications."""
        response = client.get('/api/notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['notifications'] == []
        assert data['data']['total_count'] == 0
        assert data['data']['unread_count'] == 0

    def test_get_notifications_error(self, client):
        """Test GET /api/notifications with database error."""
        # Demo API doesn't have database errors, just returns empty list
        response = client.get('/api/notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['notifications'] == []

    def test_mark_notification_read_not_implemented(self, client):
        """Test marking notification as read (not implemented yet)."""
        response = client.post(
            '/api/notifications/mark-read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response.status_code == 501
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Not implemented yet' in data['message']

    def test_get_notification_settings_not_implemented(self, client):
        """Test getting notification settings (not implemented yet)."""
        response = client.get('/api/notification-settings?user_id=test-user-123')
        assert response.status_code == 501
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Not implemented yet' in data['message']

    def test_update_notification_settings_not_implemented(self, client):
        """Test updating notification settings (not implemented yet)."""
        response = client.post(
            '/api/notification-settings/update',
            json={'user_id': 'test-user-123', 'category': 'crypto', 'enabled': True},
        )
        assert response.status_code == 501
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Not implemented yet' in data['message']
