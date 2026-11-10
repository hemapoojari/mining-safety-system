"""
WebSocket Connection Manager for Real-Time Telemetry & Alert Broadcasting
Provides live push updates to the Admin Dashboard and Worker Clients.
"""
import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("mining_safety.websocket")
router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    """Manages active WebSocket client connections for live dashboard telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcasts structured JSON payload to all connected clients.
        Supported event_types:
        - SENSOR_READING
        - RISK_UPDATE
        - WORKER_LOCATION
        - EMERGENCY_ALERT
        - EVACUATION_STATUS
        """
        if not self.active_connections:
            return

        message = {
            "event": event_type,
            "data": data,
        }

        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


ws_manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Real-time full-duplex stream for sensor telemetry, risk predictions,
    worker locations, and emergency alerts.
    """
    await ws_manager.connect(websocket)
    try:
        # Send initial connection handshake
        await websocket.send_json({
            "event": "CONNECTED",
            "data": {"message": "Connected to Mine Safety Real-Time Telemetry Stream"},
        })
        while True:
            # Keep connection alive & handle incoming pings
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("action") == "ping":
                    await websocket.send_json({"event": "PONG", "data": {}})
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
