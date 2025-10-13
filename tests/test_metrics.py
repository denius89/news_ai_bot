"""
Tests for metrics and feedback functionality.

This module tests:
- /metrics endpoint
- /api/feedback endpoint
- Digest analytics functions
- Feedback submission and aggregation
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import Flask app for testing
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.webapp import app
from database.db_models import get_digest_analytics, update_digest_feedback, save_digest_with_metrics


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_analytics():
    """Mock analytics data."""
    return {
        "generated_count": 5,
        "avg_confidence": 0.85,
        "avg_generation_time_sec": 2.3,
        "skipped_low_quality": 1,
        "feedback_count": 3,
        "avg_feedback_score": 0.8
    }


class TestMetricsEndpoint:
    """Test /metrics endpoint."""

    @patch('routes.metrics_routes.get_digest_analytics')
    def test_metrics_endpoint_success(self, mock_get_analytics, client, mock_analytics):
        """Test /metrics endpoint returns correct format."""
        mock_get_analytics.return_value = mock_analytics

        response = client.get('/metrics')

        assert response.status_code == 200
        data = response.json

        assert data["status"] == "success"
        assert "data" in data

        metrics_data = data["data"]
        assert "generated_today" in metrics_data
        assert "avg_confidence" in metrics_data
        assert "avg_generation_time_sec" in metrics_data
        assert "skipped_low_quality" in metrics_data
        assert "feedback_count" in metrics_data
        assert "avg_feedback_score" in metrics_data

        # Check values
        assert metrics_data["generated_today"] == 5
        assert metrics_data["avg_confidence"] == 0.85
        assert metrics_data["avg_generation_time_sec"] == 2.3

    @patch('routes.metrics_routes.get_digest_analytics')
    def test_metrics_endpoint_error(self, mock_get_analytics, client):
        """Test /metrics endpoint handles errors."""
        mock_get_analytics.side_effect = Exception("Database error")

        response = client.get('/metrics')

        assert response.status_code == 500
        data = response.json
        assert data["status"] == "error"
        assert "message" in data


class TestFeedbackEndpoint:
    """Test /api/feedback endpoint."""

    @patch('routes.api_routes.update_digest_feedback')
    @patch('routes.api_routes.update_daily_analytics')
    def test_feedback_submission_success(self, mock_update_analytics, mock_update_feedback, client):
        """Test successful feedback submission."""
        mock_update_feedback.return_value = True

        response = client.post('/api/feedback',
                             json={"digest_id": "test-id", "score": 0.9},
                             content_type='application/json')

        assert response.status_code == 200
        data = response.json
        assert data["status"] == "success"
        assert data["message"] == "Feedback saved"

        mock_update_feedback.assert_called_once_with("test-id", 0.9)
        mock_update_analytics.assert_called_once()

    def test_feedback_missing_data(self, client):
        """Test feedback submission with missing data."""
        response = client.post('/api/feedback',
                             json={"digest_id": "test-id"},
                             content_type='application/json')

        assert response.status_code == 400
        data = response.json
        assert data["status"] == "error"
        assert "digest_id and score are required" in data["message"]

    def test_feedback_invalid_score(self, client):
        """Test feedback submission with invalid score."""
        response = client.post('/api/feedback',
                             json={"digest_id": "test-id", "score": 1.5},
                             content_type='application/json')

        assert response.status_code == 400
        data = response.json
        assert data["status"] == "error"
        assert "score must be between 0.0 and 1.0" in data["message"]

    @patch('routes.api_routes.update_digest_feedback')
    def test_feedback_digest_not_found(self, mock_update_feedback, client):
        """Test feedback submission for non-existent digest."""
        mock_update_feedback.return_value = False

        response = client.post('/api/feedback',
                             json={"digest_id": "non-existent", "score": 0.9},
                             content_type='application/json')

        assert response.status_code == 404
        data = response.json
        assert data["status"] == "error"
        assert data["message"] == "Digest not found"


class TestHealthEndpoint:
    """Test /api/health endpoint with digest v2 status."""

    @patch('routes.api_routes.get_digest_analytics')
    def test_health_with_good_confidence(self, mock_get_analytics, client):
        """Test health endpoint with good confidence."""
        mock_get_analytics.return_value = {
            "avg_confidence": 0.8,
            "generated_count": 10
        }

        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.json
        assert data["status"] == "success"
        assert data["digest_v2_status"] == "ok"
        assert data["avg_confidence"] == 0.8
        assert data["generated_today"] == 10

    @patch('routes.api_routes.get_digest_analytics')
    def test_health_with_low_confidence(self, mock_get_analytics, client):
        """Test health endpoint with low confidence."""
        mock_get_analytics.return_value = {
            "avg_confidence": 0.4,
            "generated_count": 5
        }

        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.json
        assert data["status"] == "success"
        assert data["digest_v2_status"] == "error"
        assert data["avg_confidence"] == 0.4


class TestDigestAnalytics:
    """Test digest analytics functions."""

    @patch('database.db_models.supabase')
    def test_get_digest_analytics_success(self, mock_supabase):
        """Test successful analytics retrieval."""
        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = [{
            "generated_count": 3,
            "avg_confidence": 0.75,
            "avg_generation_time_sec": 1.8,
            "skipped_low_quality": 0,
            "feedback_count": 2,
            "avg_feedback_score": 0.9
        }]

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        analytics = get_digest_analytics()

        assert analytics["generated_count"] == 3
        assert analytics["avg_confidence"] == 0.75
        assert analytics["avg_generation_time_sec"] == 1.8
        assert analytics["skipped_low_quality"] == 0
        assert analytics["feedback_count"] == 2
        assert analytics["avg_feedback_score"] == 0.9

    @patch('database.db_models.supabase')
    def test_get_digest_analytics_no_data(self, mock_supabase):
        """Test analytics retrieval with no data."""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        analytics = get_digest_analytics()

        # Should return default values
        assert analytics["generated_count"] == 0
        assert analytics["avg_confidence"] == 0.0
        assert analytics["avg_generation_time_sec"] == 0.0
        assert analytics["skipped_low_quality"] == 0
        assert analytics["feedback_count"] == 0
        assert analytics["avg_feedback_score"] == 0.0


class TestFeedbackFunctions:
    """Test feedback-related database functions."""

    @patch('database.db_models.supabase')
    def test_update_digest_feedback_new(self, mock_supabase):
        """Test updating feedback for digest with no previous feedback."""
        # Mock current digest data (no feedback)
        mock_current = MagicMock()
        mock_current.data = [{"feedback_score": None, "feedback_count": 0}]

        # Mock update response
        mock_update = MagicMock()
        mock_update.data = [{"id": "test-id"}]

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_current
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update

        result = update_digest_feedback("test-id", 0.8)

        assert result is True

        # Verify update was called with correct values
        update_call = mock_supabase.table.return_value.update.return_value.eq.return_value.execute
        assert update_call.called

    @patch('database.db_models.supabase')
    def test_update_digest_feedback_existing(self, mock_supabase):
        """Test updating feedback for digest with existing feedback."""
        # Mock current digest data (existing feedback)
        mock_current = MagicMock()
        mock_current.data = [{"feedback_score": 0.7, "feedback_count": 2}]

        # Mock update response
        mock_update = MagicMock()
        mock_update.data = [{"id": "test-id"}]

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_current
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update

        result = update_digest_feedback("test-id", 0.9)

        assert result is True

    @patch('database.db_models.supabase')
    def test_update_digest_feedback_not_found(self, mock_supabase):
        """Test updating feedback for non-existent digest."""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        result = update_digest_feedback("non-existent", 0.8)

        assert result is False


class TestSaveDigestWithMetrics:
    """Test saving digest with metrics."""

    @patch('database.db_models.supabase')
    @patch('database.db_models.update_daily_analytics')
    def test_save_digest_with_metrics_success(self, mock_update_analytics, mock_supabase):
        """Test successful digest save with metrics."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "new-digest-id"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        digest_id = save_digest_with_metrics(
            user_id="user-123",
            summary="Test digest",
            category="tech",
            style="analytical",
            confidence=0.85,
            generation_time_sec=2.1,
            meta={"tone": "neutral", "length": "medium"}
        )

        assert digest_id == "new-digest-id"
        mock_update_analytics.assert_called_once()

    @patch('database.db_models.supabase')
    def test_save_digest_with_metrics_failure(self, mock_supabase):
        """Test digest save failure."""
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        digest_id = save_digest_with_metrics(
            user_id="user-123",
            summary="Test digest",
            category="tech",
            style="analytical",
            confidence=0.85,
            generation_time_sec=2.1,
            meta={"tone": "neutral", "length": "medium"}
        )

        assert digest_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
