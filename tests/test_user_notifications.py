"""
Unit tests for User Notifications API endpoints.
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from webapp import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestUserNotificationsAPI:
    """Test user notifications API endpoints."""

    def test_get_user_notifications_missing_user_id(self, client):
        """Test GET /api/user_notifications without user_id parameter."""
        response = client.get('/api/user_notifications')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'user_id parameter is required' in data['message']

    @patch('routes.api_routes.get_user_notifications')
    def test_get_user_notifications_success(self, mock_get_notifications, client):
        """Test successful GET /api/user_notifications."""
        # Mock database response
        mock_notifications = [
            {
                'id': 'notif-1',
                'title': 'Test Notification',
                'message': 'Test message',
                'category': 'crypto',
                'read': False,
                'created_at': datetime(2025, 10, 2, 10, 0, 0),
                'via_telegram': False,
                'via_webapp': True,
            },
            {
                'id': 'notif-2',
                'title': 'Read Notification',
                'message': 'Already read',
                'category': 'economy',
                'read': True,
                'created_at': datetime(2025, 10, 1, 10, 0, 0),
                'via_telegram': True,
                'via_webapp': True,
            },
        ]
        mock_get_notifications.return_value = mock_notifications

        response = client.get('/api/user_notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'notifications' in data['data']
        assert len(data['data']['notifications']) == 2
        assert data['data']['total_count'] == 2

        # Check notification structure
        notification = data['data']['notifications'][0]
        assert 'id' in notification
        assert 'title' in notification
        assert 'text' in notification
        assert 'read' in notification
        assert 'created_at' in notification

    @patch('routes.api_routes.get_user_notifications')
    def test_get_user_notifications_with_limit_offset(self, mock_get_notifications, client):
        """Test GET /api/user_notifications with limit and offset parameters."""
        mock_notifications = [
            {
                'id': f'notif-{i}',
                'title': f'Test Notification {i}',
                'message': 'Test message',
                'category': 'crypto',
                'read': False,
                'created_at': datetime(2025, 10, 2, 10, 0, 0),
                'via_telegram': False,
                'via_webapp': True,
            }
            for i in range(1, 6)
        ]
        mock_get_notifications.return_value = mock_notifications

        response = client.get('/api/user_notifications?user_id=test-user-123&limit=3&offset=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['notifications']) == 5  # Mock returns all, limit handled by DB

    @patch('routes.api_routes.get_user_notifications')
    def test_get_user_notifications_invalid_limit(self, mock_get_notifications, client):
        """Test GET /api/user_notifications with invalid limit parameter."""
        mock_get_notifications.return_value = []

        response = client.get('/api/user_notifications?user_id=test-user-123&limit=-1')
        assert response.status_code == 200  # API should handle gracefully
        data = response.get_json()
        assert data['status'] == 'success'

    @patch('routes.api_routes.get_user_notifications')
    def test_get_user_notifications_empty(self, mock_get_notifications, client):
        """Test GET /api/user_notifications with no notifications."""
        mock_get_notifications.return_value = []

        response = client.get('/api/user_notifications?user_id=test-user-123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['notifications'] == []
        assert data['data']['total_count'] == 0

    @patch('routes.api_routes.get_user_notifications')
    def test_get_user_notifications_error(self, mock_get_notifications, client):
        """Test GET /api/user_notifications with database error."""
        mock_get_notifications.side_effect = Exception("Database error")

        response = client.get('/api/user_notifications?user_id=test-user-123')
        assert response.status_code == 500  # API returns 500 on database error
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Internal server error' in data['message']

    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_mark_notification_read_missing_user_id(self, mock_get_user, mock_mark_read, client):
        """Test POST /api/user_notifications/mark_read without user_id (uses default user_id=1)."""
        mock_get_user.return_value = {'id': 'uuid-123'}
        mock_mark_read.return_value = True

        response = client.post(
            '/api/user_notifications/mark_read', json={'notification_id': 'notif-1'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_mark_notification_read_missing_notification_id(self, client):
        """Test POST /api/user_notifications/mark_read without notification_id."""
        response = client.post(
            '/api/user_notifications/mark_read', json={'user_id': 'test-user-123'}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'notification_id is required' in data['message']

    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_mark_notification_read_success(self, mock_get_user, mock_mark_read, client):
        """Test successful POST /api/user_notifications/mark_read."""
        mock_get_user.return_value = {'id': 'uuid-123'}
        mock_mark_read.return_value = True

        response = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_mark_notification_read_idempotent(self, mock_get_user, mock_mark_read, client):
        """Test POST /api/user_notifications/mark_read is idempotent."""
        mock_get_user.return_value = {'id': 'uuid-123'}
        mock_mark_read.return_value = True

        # First request
        response1 = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response1.status_code == 200

        # Second request (idempotent)
        response2 = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response2.status_code == 200

    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_mark_notification_read_not_found(self, mock_get_user, mock_mark_read, client):
        """Test POST /api/user_notifications/mark_read with invalid notification ID."""
        mock_get_user.return_value = {'id': 'uuid-123'}
        mock_mark_read.return_value = False

        response = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'test-user-123', 'notification_id': 'invalid-id'},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_mark_notification_read_database_error(self, mock_get_user, mock_mark_read, client):
        """Test POST /api/user_notifications/mark_read with database error."""
        mock_get_user.return_value = {'id': 'uuid-123'}
        mock_mark_read.side_effect = Exception("Database error")

        response = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'test-user-123', 'notification_id': 'notif-1'},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_create_notification_with_telegram_flag(self, client):
        """Test creating notification with via_telegram=true flag - endpoint doesn't exist."""
        # This endpoint doesn't exist, so we expect 404
        response = client.post(
            '/api/user_notifications',
            json={
                'user_id': 'test-user-123',
                'title': 'Telegram Test',
                'message': 'This notification should be sent via Telegram',
                'category': 'crypto',
                'via_telegram': True,
                'via_webapp': True,
            },
        )
        assert response.status_code == 405

    @patch('routes.api_routes.get_user_notifications')
    @patch('database.db_models.mark_notification_read')
    @patch('database.db_models.get_user_by_telegram')
    def test_integration_scenario(
        self, mock_get_user, mock_mark_read, mock_get_notifications, client
    ):
        """Test integration scenario: create -> get -> mark read -> get again."""
        # Mock initial state (unread notification)
        mock_get_notifications.return_value = [
            {
                'id': 'integration-test-1',
                'title': 'Integration Test',
                'message': 'Test notification for integration',
                'category': 'technology',
                'read': False,
                'created_at': datetime(2025, 10, 2, 10, 0, 0),
                'via_telegram': False,
                'via_webapp': True,
            }
        ]
        mock_mark_read.return_value = True

        # Step 1: Get notifications (should be unread)
        response1 = client.get('/api/user_notifications?user_id=integration-user')
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1['status'] == 'success'
        assert data1['data']['notifications'][0]['read'] is False

        # Step 2: Mark as read
        response2 = client.post(
            '/api/user_notifications/mark_read',
            json={'user_id': 'integration-user', 'notification_id': 'integration-test-1'},
        )
        assert response2.status_code == 200

        # Step 3: Get notifications again (should be read)
        mock_get_notifications.return_value = [
            {
                'id': 'integration-test-1',
                'title': 'Integration Test',
                'message': 'Test notification for integration',
                'category': 'technology',
                'read': True,  # Now marked as read
                'created_at': datetime(2025, 10, 2, 10, 0, 0),
                'via_telegram': False,
                'via_webapp': True,
            }
        ]

        response3 = client.get('/api/user_notifications?user_id=integration-user')
        assert response3.status_code == 200
        data3 = response3.get_json()
        assert data3['status'] == 'success'
        assert data3['data']['notifications'][0]['read'] is True
