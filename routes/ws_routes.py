"""
PULSE-WS: Pure FastAPI WebSocket hub for Reactor Core.
Обеспечивает real-time передачу событий между сервером и клиентами.
"""

import json
import logging
import time
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# PULSE-WS: Import reactor for event integration
from core.reactor import reactor, Events

logger = logging.getLogger(__name__)

# PULSE-WS: FastAPI router for WebSocket routes
router = APIRouter(prefix="/ws")

# PULSE-WS: Set of active WebSocket connections
active_connections: Set[WebSocket] = set()

# PULSE-WS: Connection statistics
ws_stats = {"connected_clients": 0, "events_emitted_total": 0, "last_event_timestamp": None}


@router.websocket("/stream")
async def stream(websocket: WebSocket):
    """PULSE-WS: Main WebSocket endpoint for real-time events."""
    await websocket.accept()
    active_connections.add(websocket)
    ws_stats["connected_clients"] = len(active_connections)

    client_id = id(websocket)
    logger.info(f"PULSE-WS: Client connected: {client_id}")
    logger.info(f"PULSE-WS: Total connected clients: {len(active_connections)}")

    # PULSE-WS: Send welcome message
    await websocket.send_json(
        {
            "type": "reactor_connected",
            "data": {"message": "Connected to PulseAI Reactor", "client_id": client_id, "timestamp": time.time()},
        }
    )

    try:
        while True:
            # PULSE-WS: Handle incoming messages
            data = await websocket.receive_text()

            if data == "ping":
                # PULSE-WS: Heartbeat response
                await websocket.send_text("pong")
            elif data.startswith("subscribe:"):
                # PULSE-WS: Event subscription (future feature)
                events = data.split(":", 1)[1].split(",")
                await websocket.send_json(
                    {
                        "type": "reactor_subscribed",
                        "data": {"events": events, "message": f"Subscribed to events: {events}"},
                    }
                )
            else:
                # PULSE-WS: Echo back unknown messages
                await websocket.send_json({"type": "echo", "data": {"message": data}})

    except WebSocketDisconnect:
        active_connections.discard(websocket)
        ws_stats["connected_clients"] = len(active_connections)

        logger.info(f"PULSE-WS: Client disconnected: {client_id}")
        logger.info(f"PULSE-WS: Total connected clients: {len(active_connections)}")

        # PULSE-WS: Emit disconnect event to reactor
        try:
            reactor.emit_sync(Events.WEBSOCKET_DISCONNECTED, client_id=client_id)
        except Exception as e:
            logger.error(f"PULSE-WS: Error emitting disconnect event: {e}")
    except Exception as e:
        logger.error(f"PULSE-WS: WebSocket error: {e}")
        active_connections.discard(websocket)
        ws_stats["connected_clients"] = len(active_connections)


async def ws_broadcast(event: dict):
    """PULSE-WS: Broadcast event to all connected WebSocket clients."""
    if not active_connections:
        return

    dead_connections = []
    ws_stats["events_emitted_total"] += 1
    ws_stats["last_event_timestamp"] = time.time()

    for connection in list(active_connections):
        try:
            await connection.send_json(event)
        except Exception as e:
            logger.warning(f"PULSE-WS: Failed to send to client {id(connection)}: {e}")
            dead_connections.append(connection)

    # PULSE-WS: Clean up dead connections
    for connection in dead_connections:
        active_connections.discard(connection)
        ws_stats["connected_clients"] = len(active_connections)

    logger.debug(f"PULSE-WS: Event '{event.get('type', 'unknown')}' sent to {len(active_connections)} clients")


@router.get("/status")
async def websocket_status():
    """PULSE-WS: WebSocket status endpoint."""
    return {
        "status": "active",
        "connected_clients": len(active_connections),
        "stats": ws_stats,
        "reactor_events": [
            "AI_METRICS_UPDATED",
            "NEWS_PROCESSED",
            "DIGEST_CREATED",
            "EVENT_DETECTED",
            "USER_ACTION",
            "SYSTEM_HEALTH_CHECK",
            "REACTOR_HEARTBEAT",
        ],
    }


@router.get("/stats")
async def websocket_stats():
    """PULSE-WS: WebSocket statistics endpoint."""
    return {
        "connected_clients": len(active_connections),
        "ws_active_connections": len(active_connections),
        "ws_events_emitted_total": ws_stats["events_emitted_total"],
        "ws_last_event_ts": ws_stats["last_event_timestamp"],
        "reactor_events_subscribed": 7,
    }


@router.get("/health")
async def reactor_health():
    """PULSE-WS: Reactor health check endpoint."""
    try:
        health_data = {
            "reactor": reactor.get_health(),
            "websocket": {"active_connections": len(active_connections), "stats": ws_stats},
            "timestamp": time.time(),
        }
        return health_data
    except Exception as e:
        logger.error(f"PULSE-WS: Health check error: {e}")
        return {
            "reactor": {"status": "error", "error": str(e)},
            "websocket": {"active_connections": len(active_connections), "stats": ws_stats},
            "timestamp": time.time(),
        }


def get_connected_clients_count() -> int:
    """PULSE-WS: Get number of connected clients (for compatibility)."""
    return len(active_connections)


def get_websocket_stats() -> dict:
    """PULSE-WS: Get WebSocket statistics (for compatibility)."""
    return {
        "connected_clients": len(active_connections),
        "ws_active_connections": len(active_connections),
        "ws_events_emitted_total": ws_stats["events_emitted_total"],
        "ws_last_event_ts": ws_stats["last_event_timestamp"],
        "socketio_initialized": False,  # Compatibility flag
        "reactor_events_subscribed": 7,
    }


# PULSE-WS: Export router for FastAPI app integration
__all__ = ["router", "ws_broadcast", "get_connected_clients_count", "get_websocket_stats"]
