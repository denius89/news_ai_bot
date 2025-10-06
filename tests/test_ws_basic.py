"""
PULSE-WS: Basic WebSocket tests for FastAPI integration.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from main import app


class TestWebSocketBasic:
    """PULSE-WS: Basic WebSocket functionality tests."""
    
    def test_ws_connect_and_heartbeat(self):
        """PULSE-WS: Test WebSocket connection and heartbeat."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/stream") as websocket:
            # Test heartbeat
            websocket.send_text("ping")
            response = websocket.receive_text()
            assert response == "pong"
            
            # Test JSON response
            websocket.send_text("subscribe:test_event")
            response = websocket.receive_json()
            assert response["type"] == "reactor_subscribed"
            assert "test_event" in response["data"]["events"]
    
    def test_ws_welcome_message(self):
        """PULSE-WS: Test welcome message on connection."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/stream") as websocket:
            # Should receive welcome message
            response = websocket.receive_json()
            assert response["type"] == "reactor_connected"
            assert "Connected to PulseAI Reactor" in response["data"]["message"]
    
    def test_ws_status_endpoint(self):
        """PULSE-WS: Test WebSocket status endpoint."""
        client = TestClient(app)
        
        response = client.get("/ws/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert "connected_clients" in data
        assert "stats" in data
        assert "reactor_events" in data
    
    def test_ws_stats_endpoint(self):
        """PULSE-WS: Test WebSocket stats endpoint."""
        client = TestClient(app)
        
        response = client.get("/ws/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "connected_clients" in data
        assert "ws_active_connections" in data
        assert "ws_events_emitted_total" in data
        assert "ws_last_event_ts" in data
    
    def test_ws_health_endpoint(self):
        """PULSE-WS: Test WebSocket health endpoint."""
        client = TestClient(app)
        
        response = client.get("/ws/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "reactor" in data
        assert "websocket" in data
        assert "timestamp" in data


class TestWebSocketIntegration:
    """PULSE-WS: Integration tests with Reactor."""
    
    def test_reactor_events_broadcast(self):
        """PULSE-WS: Test that Reactor events are broadcast via WebSocket."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/stream") as websocket:
            # Clear welcome message
            websocket.receive_json()
            
            # Emit a test event via Reactor
            from core.reactor import reactor
            reactor.emit_sync("test_event", message="Hello WebSocket!")
            
            # Should receive the event via WebSocket
            response = websocket.receive_json()
            assert response["type"] == "test_event"
            assert response["data"]["message"] == "Hello WebSocket!"
    
    def test_multiple_connections(self):
        """PULSE-WS: Test multiple WebSocket connections."""
        client = TestClient(app)
        
        # Connect multiple clients
        with client.websocket_connect("/ws/stream") as ws1:
            with client.websocket_connect("/ws/stream") as ws2:
                # Clear welcome messages
                ws1.receive_json()
                ws2.receive_json()
                
                # Check stats show 2 connections
                response = client.get("/ws/stats")
                data = response.json()
                assert data["connected_clients"] == 2
                
                # Emit event and both should receive it
                from core.reactor import reactor
                reactor.emit_sync("test_multiple", message="Broadcast test")
                
                response1 = ws1.receive_json()
                response2 = ws2.receive_json()
                
                assert response1["type"] == "test_multiple"
                assert response2["type"] == "test_multiple"
                assert response1["data"]["message"] == "Broadcast test"
                assert response2["data"]["message"] == "Broadcast test"


if __name__ == "__main__":
    pytest.main([__file__])
