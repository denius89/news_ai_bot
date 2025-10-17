"""
Unit tests for Subscriptions API endpoints.
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


class TestSubscriptionsAPI:
    """Test subscriptions API endpoints."""

    def test_get_subscriptions_missing_user_id(self, client, mock_auth):
        """Test GET /api/subscriptions without user_id parameter."""
        response = client.get("/api/subscriptions")
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data["status"] == "error"
            assert "user_id parameter is required" in data["message"]
        else:
            assert response.status_code == 400

    @patch("services.subscription_service.SubscriptionService.list")
    def test_get_subscriptions_success(self, mock_list, client, mock_auth):
        """Test successful GET /api/subscriptions."""
        # Mock service response
        mock_list.return_value = [{"category": "crypto"}, {"category": "economy"}]

        response = client.get("/api/subscriptions?user_id=123")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "categories" in data["data"]
        assert "total_subscriptions" in data["data"]
        assert data["data"]["total_subscriptions"] == 2

    def test_update_subscription_missing_json(self, client, mock_auth):
        """Test POST /api/subscriptions/update without JSON body."""
        response = client.post("/api/subscriptions/update", content_type="application/json")
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data["status"] == "error"
            assert "JSON body is required" in data["message"]
        else:
            assert response.status_code == 400

    def test_update_subscription_missing_fields(self, client, mock_auth):
        """Test POST /api/subscriptions/update with missing fields."""
        response = client.post("/api/subscriptions/update", json={"user_id": "123"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "required" in data["message"]

    def test_update_subscription_invalid_category(self, client, mock_auth):
        """Test POST /api/subscriptions/update with invalid category."""
        response = client.post(
            "/api/subscriptions/update",
            json={"user_id": "123", "category": "invalid_category", "enabled": True},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Invalid category" in data["message"]

    @patch("services.subscription_service.SubscriptionService.add")
    def test_update_subscription_enable_success(self, mock_add, client, mock_auth):
        """Test successful subscription enable."""
        mock_add.return_value = True

        response = client.post(
            "/api/subscriptions/update",
            json={"user_id": "123", "category": "crypto", "enabled": True},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "subscribed to" in data["message"]

    @patch("services.subscription_service.SubscriptionService.remove")
    def test_update_subscription_disable_success(self, mock_remove, client, mock_auth):
        """Test successful subscription disable."""
        mock_remove.return_value = True

        response = client.post(
            "/api/subscriptions/update",
            json={"user_id": "123", "category": "crypto", "enabled": False},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "unsubscribed from" in data["message"]

    def test_create_user_missing_json(self, client, mock_auth):
        """Test POST /api/users without JSON body."""
        response = client.post("/api/users", content_type="application/json")
        assert response.status_code == 400
        data = response.get_json()
        if data:
            assert data["status"] == "error"
            assert "JSON body is required" in data["message"]
        else:
            assert response.status_code == 400

    def test_create_user_missing_telegram_id(self, client, mock_auth):
        """Test POST /api/users without telegram_id."""
        response = client.post("/api/users", json={"username": "test"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "telegram_id is required" in data["message"]

    @patch("services.subscription_service.SubscriptionService.get_or_create_user")
    def test_create_user_success(self, mock_get_user, client, mock_auth):
        """Test successful user creation."""
        mock_get_user.return_value = "user-uuid-123"

        response = client.post("/api/users", json={"telegram_id": 123456789, "username": "testuser"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["data"]["user_id"] == "user-uuid-123"
        assert data["data"]["telegram_id"] == 123456789

    def test_health_check(self, client, mock_auth):
        """Test GET /api/health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "healthy" in data["message"]
        assert "version" in data
