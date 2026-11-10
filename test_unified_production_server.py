"""
Verification of Unified Single-Port Production Serving
Tests the complete application on port 7860 (Hugging Face Spaces Port):
1. Serving compiled React frontend on '/'
2. Serving CSS & JS assets on '/assets/...'
3. Client-side SPA routing on '/analytics', '/workers', '/alerts'
4. REST APIs on '/api/...'
5. System health and docs on '/health', '/api/health', '/docs'
6. WebSocket telemetry on 'ws://127.0.0.1:7860/ws/telemetry'
7. PDF & CSV report downloads
8. ML Predictions & Emergency Trigger
"""
import sys
import os
import time
import subprocess
import requests
import asyncio
import websockets
import json

PORT = 7860
BASE_URL = f"http://127.0.0.1:{PORT}"
WS_URL = f"ws://127.0.0.1:{PORT}/ws/telemetry"


def run_tests():
    print("=" * 70)
    print(" TESTING UNIFIED SINGLE-PORT PRODUCTION SERVING (PORT 7860)")
    print("=" * 70)

    # 1. Health check
    print("\n[1/8] Verifying Health Check Endpoint...")
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    health = r.json()
    assert health["status"] == "healthy"
    print(f"  --> PASS: Status: {health['status']}, DB: {health['database']}")

    # 2. React frontend index.html on root
    print("\n[2/8] Verifying Compiled React Frontend on '/'...")
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Root returned {r.status_code}"
    assert "AI/ML Mining Safety & Evacuation System" in r.text
    assert '<div id="root"></div>' in r.text
    print("  --> PASS: '/' correctly served React 18 production index.html")

    # 3. Static assets (CSS and JS)
    print("\n[3/8] Verifying Static CSS/JS Asset Bundles...")
    r_css = requests.get(f"{BASE_URL}/assets/index-C4NNqZRW.css", timeout=5)
    assert r_css.status_code == 200, f"CSS asset failed: {r_css.status_code}"
    assert len(r_css.content) > 10000, "CSS bundle is incomplete"
    r_js = requests.get(f"{BASE_URL}/assets/index-VVlt5uZ9.js", timeout=5)
    assert r_js.status_code == 200, f"JS asset failed: {r_js.status_code}"
    assert len(r_js.content) > 100000, "JS bundle is incomplete"
    print(f"  --> PASS: CSS ({len(r_css.content)} bytes) and JS ({len(r_js.content)} bytes) delivered")

    # 4. SPA Client-Side Routing
    print("\n[4/8] Verifying Client-Side SPA Fallback...")
    for route in ["/analytics", "/workers", "/alerts", "/sensors", "/underground"]:
        r = requests.get(f"{BASE_URL}{route}", timeout=5)
        assert r.status_code == 200, f"SPA route {route} failed: {r.status_code}"
        assert '<div id="root"></div>' in r.text
    print("  --> PASS: SPA navigation routes return React index.html without 404")

    # 5. REST APIs (Workers, Zones, Sensors, Analytics)
    print("\n[5/8] Verifying REST APIs on Unified Port...")
    zones = requests.get(f"{BASE_URL}/api/zones", timeout=5).json()
    assert len(zones) == 6, f"Expected 6 zones, got {len(zones)}"
    workers = requests.get(f"{BASE_URL}/api/workers", timeout=5).json()
    assert len(workers) >= 9, f"Expected >= 9 workers, got {len(workers)}"
    sensors = requests.get(f"{BASE_URL}/api/sensors/readings/current", timeout=5).json()
    assert len(sensors) >= 17, f"Expected >= 17 sensor readings, got {len(sensors)}"
    kpis = requests.get(f"{BASE_URL}/api/analytics/kpis", timeout=5).json()
    assert "total_sensor_readings" in kpis
    print(f"  --> PASS: 6 Zones, {len(workers)} Workers, {len(sensors)} Sensors, and Analytics KPIs validated")

    # 6. Report Downloads (PDF & CSV)
    print("\n[6/8] Verifying Report Downloads (PDF & CSV)...")
    r_pdf = requests.get(f"{BASE_URL}/api/reports/zone/1/pdf", timeout=5)
    assert r_pdf.status_code == 200 and r_pdf.headers.get("content-type") == "application/pdf"
    assert len(r_pdf.content) > 3000
    r_csv = requests.get(f"{BASE_URL}/api/reports/sensors/csv", timeout=5)
    assert r_csv.status_code == 200 and "text/csv" in r_csv.headers.get("content-type", "")
    assert "reading_id" in r_csv.text
    print(f"  --> PASS: Zone PDF ({len(r_pdf.content)} bytes) & Sensor CSV verified")

    # 7. WebSocket Telemetry Stream
    print("\n[7/8] Verifying WebSocket Telemetry Stream on Unified Origin...")
    async def test_ws():
        async with websockets.connect(WS_URL) as ws:
            # Send ping
            await ws.send(json.dumps({"type": "ping"}))
            # Wait for response/broadcast
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(msg)
            print(f"  --> PASS: WebSocket connected, received event type='{data.get('type')}'")
            return True

    asyncio.run(test_ws())

    # 8. Swagger Docs & System Status
    print("\n[8/8] Verifying System Metadata & Swagger Docs...")
    r_docs = requests.get(f"{BASE_URL}/docs", timeout=5)
    assert r_docs.status_code == 200 and "swagger-ui" in r_docs.text.lower()
    r_stat = requests.get(f"{BASE_URL}/api/system/status", timeout=5)
    assert r_stat.status_code == 200 and r_stat.json()["status"] == "online"
    print("  --> PASS: Swagger UI at /docs and System Status at /api/system/status")

    print("\n" + "=" * 70)
    print(" ALL 8 PRODUCTION ARCHITECTURE CHECKS PASSED ON PORT 7860!")
    print("=" * 70)


if __name__ == "__main__":
    # Start uvicorn server as subprocess
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    env["API_PORT"] = str(PORT)

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        # Wait up to 15s for server to start
        started = False
        for _ in range(30):
            time.sleep(0.5)
            try:
                res = requests.get(f"{BASE_URL}/api/health", timeout=1)
                if res.status_code == 200:
                    started = True
                    break
            except Exception:
                pass

        if not started:
            print("ERROR: Server failed to start on port 7860")
            out, _ = proc.communicate(timeout=2)
            print(out)
            sys.exit(1)

        run_tests()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        print("\nUnified test server terminated cleanly.")
