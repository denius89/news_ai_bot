"""
Unit tests for Subscriptions API endpoints.
"""

import pytest

from webapp import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSubscriptionsAPI:
    """Test subscriptions API endpoints."""

    def test_get_subscriptions_missing_user_id(self, client):
        """Test GET /api/subscriptions without user_id parameter."""
        response = client.get('/api/subscriptions')
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data['status'] == 'error'
            assert 'user_id parameter is required' in data['message']
        else:
            assert response.status_code == 400

    def test_get_subscriptions_success(self, client):
        """Test successful GET /api/subscriptions."""
        response = client.get('/api/subscriptions?user_id=123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'categories' in data['data']
        assert 'total_subscriptions' in data['data']
        assert data['data']['total_subscriptions'] == 0  # Demo returns empty subscriptions

    def test_update_subscription_missing_json(self, client):
        """Test POST /api/subscriptions/update without JSON body."""
        response = client.post('/api/subscriptions/update', content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data['status'] == 'error'
            assert 'JSON body is required' in data['message']
        else:
            assert response.status_code == 400

    def test_update_subscription_missing_fields(self, client):
        """Test POST /api/subscriptions/update with missing fields."""
        response = client.post('/api/subscriptions/update', json={'user_id': '123'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'required' in data['message']

    def test_update_subscription_invalid_category(self, client):
        """Test POST /api/subscriptions/update with invalid category."""
        response = client.post(
            '/api/subscriptions/update',
            json={'user_id': '123', 'category': 'invalid_category', 'enabled': True},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Invalid category' in data['message']

    def test_update_subscription_enable_success(self, client):
        """Test successful subscription enable."""
        response = client.post(
            '/api/subscriptions/update',
            json={'user_id': '123', 'category': 'crypto', 'enabled': True},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'subscribed to' in data['message']

    def test_update_subscription_disable_success(self, client):
        """Test successful subscription disable."""
        response = client.post(
            '/api/subscriptions/update',
            json={'user_id': '123', 'category': 'crypto', 'enabled': False},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'unsubscribed from' in data['message']

    def test_create_user_missing_json(self, client):
        """Test POST /api/users without JSON body."""
        response = client.post('/api/users', content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data['status'] == 'error'
            assert 'JSON body is required' in data['message']
        else:
            assert response.status_code == 400

    def test_create_user_missing_telegram_id(self, client):
        """Test POST /api/users without telegram_id."""
        response = client.post('/api/users', json={'username': 'test'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'telegram_id is required' in data['message']

    def test_create_user_success(self, client):
        """Test successful user creation."""
        response = client.post(
            '/api/users', json={'telegram_id': 123456789, 'username': 'testuser'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'user_id' in data['data']
        assert data['data']['telegram_id'] == 123456789

    def test_health_check(self, client):
        """Test GET /api/health endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'healthy' in data['message']
        assert 'version' in data
