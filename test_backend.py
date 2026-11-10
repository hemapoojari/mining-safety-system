"""
Automated Backend Verification Suite
Tests all REST APIs, Database Creation, Seeding, Risk Assessment, Geofencing,
Emergency Alerts, 2-Way Worker ACKs, and WebSocket connectivity.
"""
import sys
import logging
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.database.models import MiningZone, Worker, Sensor, EmergencyAlert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend_test")


def run_all_tests():
    logger.info("==================================================")
    logger.info("STARTING BACKEND VERIFICATION TEST SUITE")
    logger.info("==================================================")

    # Use TestClient with lifespan context
    with TestClient(app) as client:
        # TEST 1: Health Check Endpoint
        logger.info("\n--- TEST 1: Health Check ---")
        res = client.get("/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["status"] == "healthy", f"Database not healthy: {data}"
        logger.info(f"PASSED: Health check returned {data}")

        # TEST 2: Verify Database Seeding
        logger.info("\n--- TEST 2: Database Seeding Verification ---")
        res_zones = client.get("/api/zones/")
        assert res_zones.status_code == 200
        zones = res_zones.json()
        assert len(zones) >= 6, f"Expected at least 6 seeded zones, got {len(zones)}"
        open_pit_zones = [z for z in zones if z["mine_type"] == "open_pit"]
        ug_zones = [z for z in zones if z["mine_type"] == "underground"]
        assert len(open_pit_zones) >= 3, "Missing open-pit zones"
        assert len(ug_zones) >= 3, "Missing underground zones"
        logger.info(f"PASSED: Found {len(open_pit_zones)} Open-Pit and {len(ug_zones)} Underground zones.")

        res_workers = client.get("/api/workers/")
        assert res_workers.status_code == 200
        workers = res_workers.json()
        assert len(workers) >= 7, f"Expected at least 7 seeded workers, got {len(workers)}"
        logger.info(f"PASSED: Found {len(workers)} registered workers.")

        res_sensors = client.get("/api/sensors/")
        assert res_sensors.status_code == 200
        sensors = res_sensors.json()
        assert len(sensors) >= 12, f"Expected at least 12 sensors, got {len(sensors)}"
        logger.info(f"PASSED: Found {len(sensors)} registered sensors.")

        res_curr = client.get("/api/sensors/readings/current")
        assert res_curr.status_code == 200
        readings = res_curr.json()
        assert len(readings) >= 12, "Current readings not populated"
        logger.info(f"PASSED: Current readings retrieved for {len(readings)} sensors.")

        # TEST 3: Worker Registration & Location Geofencing
        logger.info("\n--- TEST 3: Worker Registration & Spatial Geofence Resolution ---")
        import uuid
        test_worker_code = f"WRK-TEST-{uuid.uuid4().hex[:4].upper()}"
        new_worker_payload = {
            "worker_code": test_worker_code,
            "full_name": "Test Safety Engineer",
            "role": "Safety Officer",
            "phone": "+91-9999900000",
            "current_lat": 23.7462,
            "current_lng": 86.4152,
            "elevation_or_level": "Bench #1 Upper",
            "status": "active",
        }
        res_create_w = client.post("/api/workers/", json=new_worker_payload)
        assert res_create_w.status_code == 201, f"Worker create failed: {res_create_w.text}"
        w_data = res_create_w.json()
        worker_id = w_data["id"]
        logger.info(f"PASSED: Registered worker {test_worker_code} (ID: {worker_id}).")

        # Update location with coordinates inside zone OP-Z1
        loc_payload = {
            "current_lat": 23.7463,
            "current_lng": 86.4153,
            "elevation_or_level": "Bench #1 Upper Face",
        }
        res_loc = client.post(f"/api/workers/{worker_id}/location", json=loc_payload)
        assert res_loc.status_code == 200
        w_updated = res_loc.json()
        assert w_updated["zone_name"] == "North Bench #1 (Upper Wall)", f"Geofence resolution mismatch: {w_updated}"
        logger.info(f"PASSED: Geofence successfully resolved location to '{w_updated['zone_name']}'.")

        # TEST 4: Sensor Submission & Risk Assessment (Normal vs Critical)
        logger.info("\n--- TEST 4: Sensor Ingestion & Dual-Engine Risk Assessment ---")
        # Submit nominal reading in OP-Z1
        nominal_reading = {
            "sensor_code": "SLOPE-01",
            "zone_id": 1,
            "mine_type": "open_pit",
            "sensor_type": "slope_displacement",
            "value": 0.25,
            "unit": "mm",
        }
        res_norm = client.post("/api/sensors/readings", json=nominal_reading)
        assert res_norm.status_code == 201
        logger.info("PASSED: Nominal reading submitted successfully.")

        # Query Zone Risk Details
        res_risk = client.get("/api/zones/1/risk")
        assert res_risk.status_code == 200
        risk_data = res_risk.json()
        assert risk_data["current_risk_tier"] == "Safe", f"Expected Safe tier, got {risk_data['current_risk_tier']}"
        logger.info(f"PASSED: Zone 1 Risk Level is '{risk_data['current_risk_tier']}' (Score: {risk_data['composite_risk_score']}).")

        # Submit CRITICAL reading to trigger emergency response
        logger.info("\n--- TEST 5: Critical Hazard & Automated Targeted Evacuation ---")
        critical_reading = {
            "sensor_code": "SLOPE-01",
            "zone_id": 1,
            "mine_type": "open_pit",
            "sensor_type": "slope_displacement",
            "value": 16.5,  # Exceeds 12.0 mm critical threshold
            "unit": "mm",
        }
        res_crit = client.post("/api/sensors/readings", json=critical_reading)
        assert res_crit.status_code == 201

        # Check that Zone 1 escalated to Critical
        res_z1 = client.get("/api/zones/1")
        assert res_z1.status_code == 200
        assert res_z1.json()["current_risk_tier"] == "Critical", f"Expected Critical, got {res_z1.json()['current_risk_tier']}"
        logger.info("PASSED: Zone 1 escalated to CRITICAL.")

        # Verify active emergency alert was triggered
        res_active_alerts = client.get("/api/alerts/active")
        assert res_active_alerts.status_code == 200
        active_alerts = res_active_alerts.json()
        assert len(active_alerts) >= 1, "Expected active alert"
        target_alert = [a for a in active_alerts if a["zone_id"] == 1][0]
        alert_id = target_alert["id"]
        logger.info(f"PASSED: Critical Emergency Alert auto-triggered: Code {target_alert['alert_code']}, Affected Workers: {target_alert['affected_workers_count']}.")

        # TEST 6: 2-Way Worker Acknowledgement & Evacuation Tracking
        logger.info("\n--- TEST 6: Worker Evacuation Acknowledgement & Tracking ---")
        # Step A: Worker acknowledges and starts evacuating
        ack_payload = {
            "worker_id": worker_id,
            "status": "evacuating",
            "notes": "Leaving Bench 1 towards Safe Muster Point A",
        }
        res_ack = client.post(f"/api/alerts/{alert_id}/acknowledge", json=ack_payload)
        assert res_ack.status_code == 200
        assert res_ack.json()["worker_status"] == "evacuating"
        logger.info("PASSED: Worker ACK 'evacuating' processed.")

        # Step B: Worker reaches safe refuge / muster point
        safe_payload = {
            "worker_id": worker_id,
            "status": "safe",
            "notes": "Arrived at Surface Assembly Station",
        }
        res_safe = client.post(f"/api/alerts/{alert_id}/acknowledge", json=safe_payload)
        assert res_safe.status_code == 200
        assert res_safe.json()["worker_status"] == "safe"
        assert res_safe.json()["evacuated_safe_count"] >= 1
        logger.info(f"PASSED: Worker status updated to 'safe'. Total Safe Count: {res_safe.json()['evacuated_safe_count']}.")

        # Verify detailed evacuation status
        res_status = client.get(f"/api/alerts/{alert_id}/evacuation-status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        assert status_data["evacuated_safe_count"] >= 1
        logger.info(f"PASSED: Evacuation status breakdown verified: {status_data['acknowledged_count']} Acknowledged, {status_data['evacuated_safe_count']} Safe.")

        # TEST 7: Resolve Alert
        logger.info("\n--- TEST 7: Alert Resolution & Standdown ---")
        res_resolve = client.post(f"/api/alerts/{alert_id}/resolve")
        assert res_resolve.status_code == 200
        assert res_resolve.json()["is_active"] is False
        logger.info(f"PASSED: Alert {alert_id} resolved successfully.")

        # TEST 8: WebSocket Real-Time Telemetry Stream
        logger.info("\n--- TEST 8: WebSocket Connection & Handshake ---")
        with client.websocket_connect("/ws/telemetry") as websocket:
            # Check initial handshake message
            init_msg = websocket.receive_json()
            assert init_msg["event"] == "CONNECTED"
            logger.info(f"PASSED: WebSocket initial handshake received: {init_msg}")

            # Send ping
            websocket.send_json({"action": "ping"})
            pong_msg = websocket.receive_json()
            assert pong_msg["event"] == "PONG"
            logger.info("PASSED: WebSocket ping/pong responded correctly.")

        # TEST 9: Real-Time Simulation Tick Generation
        logger.info("\n--- TEST 9: Simulation Stream Tick Generator ---")
        res_tick = client.post("/api/sensors/simulate-tick")
        assert res_tick.status_code == 200
        tick_data = res_tick.json()
        assert tick_data["readings_generated"] >= 6
        logger.info(f"PASSED: Simulation tick generated {tick_data['readings_generated']} sensor readings across {tick_data['zones_processed']} zones.")

    logger.info("\n==================================================")
    logger.info("ALL BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY (9/9)!")
    logger.info("==================================================")



if __name__ == "__main__":
    run_all_tests()
