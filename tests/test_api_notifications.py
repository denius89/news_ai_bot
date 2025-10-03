"""
Unit tests for Notifications API endpoints.
"""

import pytest
from unittest.mock import patch

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

    @patch('database.db_models.get_user_notifications')
    def test_get_notifications_success(self, mock_get_notifications, client):
        """Test successful GET /api/notifications."""
        # Mock database response
        mock_get_notifications.return_value = [
            {
                'id': 'notif-1',
                'title': 'Test Notification',
                'message': 'Test message',
                'category': 'crypto',
                'read': False,
                'created_at': '2025-10-02T10:00:00Z',
            },
            {
                'id': 'notif-2',
                'title': 'Read Notification',
                'message': 'Already read',
                'category': 'economy',
                'read': True,
                'created_at': '2025-10-01T10:00:00Z',
            },
        ]

        response = client.get('/api/notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'notifications' in data['data']
        assert data['data']['total_count'] == 2
        assert data['data']['unread_count'] == 1

    @patch('database.db_models.get_user_notifications')
    def test_get_notifications_empty(self, mock_get_notifications, client):
        """Test GET /api/notifications with no notifications."""
        mock_get_notifications.return_value = []

        response = client.get('/api/notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['notifications'] == []
        assert data['data']['total_count'] == 0
        assert data['data']['unread_count'] == 0

    @patch('database.db_models.get_user_notifications')
    def test_get_notifications_error(self, mock_get_notifications, client):
        """Test GET /api/notifications with database error."""
        mock_get_notifications.side_effect = Exception("Database error")

        response = client.get('/api/notifications?user_id=test-user-123')
        # API should return success with empty data on error (graceful degradation)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['notifications'] == []

    def test_mark_notification_read_missing_json(self, client):
        """Test POST /api/notifications/mark-read without JSON body."""
        response = client.post('/api/notifications/mark-read', content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'JSON body is required' in data['message']

    def test_mark_notification_read_missing_fields(self, client):
        """Test POST /api/notifications/mark-read with missing fields."""
        response = client.post('/api/notifications/mark-read', json={'user_id': 'test-user'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'required' in data['message']

    @patch('database.db_models.mark_notification_read')
    def test_mark_notification_read_success(self, mock_mark_read, client):
        """Test successful notification mark as read."""
        mock_mark_read.return_value = True

        response = client.post(
            '/api/notifications/mark-read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'marked as read' in data['message']
        assert data['data']['user_id'] == 'test-user-123'
        assert data['data']['notification_id'] == 'notif-1'

    @patch('database.db_models.mark_notification_read')
    def test_mark_notification_read_not_found(self, mock_mark_read, client):
        """Test marking non-existent notification as read."""
        mock_mark_read.return_value = False

        response = client.post(
            '/api/notifications/mark-read',
            json={'user_id': 'test-user-123', 'notification_id': 'nonexistent'},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'not found' in data['message']

    def test_get_notification_settings_missing_user_id(self, client):
        """Test GET /api/notification-settings without user_id parameter."""
        response = client.get('/api/notification-settings')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'user_id parameter is required' in data['message']

    @patch('database.db_models.get_notification_settings')
    def test_get_notification_settings_success(self, mock_get_settings, client):
        """Test successful GET /api/notification-settings."""
        mock_get_settings.return_value = [
            {'category': 'crypto', 'enabled': True, 'via_telegram': True, 'via_webapp': True},
            {'category': 'economy', 'enabled': False, 'via_telegram': False, 'via_webapp': True},
        ]

        response = client.get('/api/notification-settings?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'categories' in data['data']
        assert len(data['data']['categories']) == 5  # All categories with defaults

    def test_update_notification_settings_missing_json(self, client):
        """Test POST /api/notification-settings/update without JSON body."""
        response = client.post('/api/notification-settings/update', content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'JSON body is required' in data['message']

    def test_update_notification_settings_missing_fields(self, client):
        """Test POST /api/notification-settings/update with missing fields."""
        response = client.post('/api/notification-settings/update', json={'user_id': 'test-user'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'required' in data['message']

    def test_update_notification_settings_invalid_category(self, client):
        """Test POST /api/notification-settings/update with invalid category."""
        response = client.post(
            '/api/notification-settings/update',
            json={
                'user_id': 'test-user',
                'category': 'invalid_category',
                'enabled': True,
                'via_telegram': True,
                'via_webapp': True,
            },
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Invalid category' in data['message']

    @patch('database.db_models.upsert_notification_setting')
    def test_update_notification_settings_success(self, mock_upsert, client):
        """Test successful notification settings update."""
        mock_upsert.return_value = True

        response = client.post(
            '/api/notification-settings/update',
            json={
                'user_id': 'test-user-123',
                'category': 'crypto',
                'enabled': True,
                'via_telegram': True,
                'via_webapp': False,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'updated' in data['message']
        assert data['data']['category'] == 'crypto'
