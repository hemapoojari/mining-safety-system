import urllib.request
import json
import asyncio
import websockets

def test_http():
    # Frontend HTML
    with urllib.request.urlopen("http://localhost:5173/") as resp:
        html = resp.read().decode("utf-8")
        assert "root" in html
        print("[PASS] Frontend Dashboard loaded successfully (HTTP 200, root container present)")

    # Backend OpenAPI Docs
    with urllib.request.urlopen("http://127.0.0.1:8000/docs") as resp:
        assert resp.status == 200
        print("[PASS] Backend OpenAPI Docs loaded successfully (HTTP 200)")

    # Simulation Status
    with urllib.request.urlopen("http://127.0.0.1:8000/api/simulation/status") as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("[PASS] Simulation Status endpoint operational:", data)

    # Zones API
    with urllib.request.urlopen("http://127.0.0.1:8000/api/zones") as resp:
        zones = json.loads(resp.read().decode("utf-8"))
        assert len(zones) == 6
        print(f"[PASS] Zones API returned {len(zones)} zones successfully")

    # Workers API
    with urllib.request.urlopen("http://127.0.0.1:8000/api/workers") as resp:
        workers = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] Workers API returned {len(workers)} workers successfully")

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws/telemetry"
    async with websockets.connect(uri) as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        data = json.loads(msg)
        assert data.get("event") == "CONNECTED"
        print("[PASS] Live WebSocket handshake verified on ws://127.0.0.1:8000/ws/telemetry:", data)

if __name__ == "__main__":
    test_http()
    asyncio.run(test_ws())
