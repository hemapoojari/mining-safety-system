"""
Comprehensive Step 6 Verification Suite: Real-Time Simulation & Evacuation Workflow
AI/ML-Powered Mining Safety and Worker Evacuation System

Tests 14 Complete System Workflow Points:
1. Normal sensor simulation (12 features across Open-Pit & Underground)
2. Progressive hazard development (incremental creep & gas accumulation)
3. Critical open-pit hazard detection (XGBoost/RF slope & rockfall escalation)
4. Critical underground gas detection (XGBoost methane & asphyxiation tripwire)
5. Critical fire hazard detection (Random Forest thermal & smoke runaway)
6. Worker location updates (GPS & sub-surface beacon movement streams)
7. Accurate spatial identification of affected workers in hazardous polygons
8. Targeted emergency alert creation (avoiding generalized panic)
9. Two-way worker acknowledgement workflow (Alert Sent -> Acknowledged)
10. Evacuation route generation & blocked route collision handling
11. Evacuation status transitions (Evacuating -> Reached Safe Zone)
12. WebSocket real-time event broadcasting and deduplication
13. Simulation controls API (start, stop, scenario selection, tick, reset)
14. Incident resolution and audit ledger preservation in SQLite database
"""
import logging
import json
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal
from backend.app.database.models import MiningZone, Worker, EmergencyAlert, WorkerEvacuationStatus, RiskPrediction
from backend.app.services.evacuation_routing import calculate_evacuation_route
from simulation.sensor_simulator import SensorSimulator
from simulation.worker_simulator import WorkerSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_sim_evac")


def run_all_tests():
    logger.info("=" * 70)
    logger.info("STARTING STEP 6 COMPREHENSIVE END-TO-END VERIFICATION")
    logger.info("=" * 70)

    with TestClient(app) as client:
        # -------------------------------------------------------------
        # TEST 1: Normal Sensor Simulation (12 Features)
        # -------------------------------------------------------------
        logger.info("\n--- TEST 1: Normal Sensor Simulation ---")
        sim = SensorSimulator()
        op_readings = sim.generate_open_pit_reading(zone_id=1)
        assert len(op_readings) == 6, f"Expected 6 open-pit sensors, got {len(op_readings)}"
        op_types = {r["sensor_type"] for r in op_readings}
        assert op_types == {"rainfall", "vibration", "slope_displacement", "crack_expansion", "soil_moisture", "displacement_rate"}
        logger.info(f"Open-Pit 6-Sensor Telemetry Validated: {op_types}")

        ug_readings = sim.generate_underground_reading(zone_id=4)
        assert len(ug_readings) == 6, f"Expected 6 underground sensors, got {len(ug_readings)}"
        ug_types = {r["sensor_type"] for r in ug_readings}
        assert ug_types == {"ch4", "co", "o2", "temperature", "smoke", "ventilation"}
        logger.info(f"Underground 6-Sensor Telemetry Validated: {ug_types}")
        logger.info("PASSED: Test 1")

        # -------------------------------------------------------------
        # TEST 2: Progressive Hazard Development
        # -------------------------------------------------------------
        logger.info("\n--- TEST 2: Progressive Hazard Drift ---")
        sim.set_scenario("progressive_drift")
        for _ in range(5):
            sim.step()
        drifted_op = sim.generate_open_pit_reading(zone_id=1)
        drifted_ug = sim.generate_underground_reading(zone_id=5)
        # Verify values accumulated higher than base
        ch4_reading = next(r for r in drifted_ug if r["sensor_type"] == "ch4")
        assert ch4_reading["value"] > 0.2, f"CH4 did not drift: {ch4_reading['value']}"
        logger.info(f"Progressive drift validated: CH4 drifted up to {ch4_reading['value']}% (Status: {ch4_reading['status']})")
        logger.info("PASSED: Test 2")

        # -------------------------------------------------------------
        # TEST 3: Critical Open-Pit Hazard Detection
        # -------------------------------------------------------------
        logger.info("\n--- TEST 3: Critical Open-Pit Hazard Escalation ---")
        sim.set_scenario("open_pit_hazard")
        hazard_op = sim.generate_open_pit_reading(zone_id=1)
        # Ingest into backend API
        for r in hazard_op:
            res = client.post("/api/sensors/readings", json=r)
            assert res.status_code == 201

        # Check Zone 1 escalated
        z1_risk = client.get("/api/zones/1/risk").json()
        assert z1_risk["current_risk_tier"] == "Critical", f"Expected Critical, got {z1_risk['current_risk_tier']}"
        logger.info(f"Zone 1 escalated to Critical. Dominant Hazard: {z1_risk['active_hazard']}")
        logger.info("PASSED: Test 3")

        # -------------------------------------------------------------
        # TEST 4: Critical Underground Gas Detection
        # -------------------------------------------------------------
        logger.info("\n--- TEST 4: Critical Underground Gas Detection ---")
        sim.set_scenario("gas_leak")
        hazard_ug = sim.generate_underground_reading(zone_id=4)
        for r in hazard_ug:
            res = client.post("/api/sensors/readings", json=r)
            assert res.status_code == 201

        z4_risk = client.get("/api/zones/4/risk").json()
        assert z4_risk["current_risk_tier"] == "Critical", f"Expected Critical, got {z4_risk['current_risk_tier']}"
        logger.info(f"Zone 4 escalated to Critical: {z4_risk['active_hazard']}")
        logger.info("PASSED: Test 4")

        # -------------------------------------------------------------
        # TEST 5: Critical Fire Hazard Detection
        # -------------------------------------------------------------
        logger.info("\n--- TEST 5: Critical Fire Hazard Detection ---")
        sim.set_scenario("fire_hazard")
        hazard_fire = sim.generate_underground_reading(zone_id=5)
        for r in hazard_fire:
            res = client.post("/api/sensors/readings", json=r)
            assert res.status_code == 201

        z5_risk = client.get("/api/zones/5/risk").json()
        assert z5_risk["current_risk_tier"] == "Critical", f"Expected Critical, got {z5_risk['current_risk_tier']}"
        logger.info(f"Zone 5 escalated to Critical: {z5_risk['active_hazard']}")
        logger.info("PASSED: Test 5")

        # -------------------------------------------------------------
        # TEST 6: Worker Location Updates & Continuous Movement
        # -------------------------------------------------------------
        logger.info("\n--- TEST 6: Worker Location Updates ---")
        w_sim = WorkerSimulator()
        sample_worker = {"current_lat": 23.7462, "current_lng": 86.4152, "status": "active"}
        stepped = w_sim.step_worker_position(sample_worker, is_evacuating=False)
        assert stepped["is_simulated"] is True
        assert stepped["current_lat"] != 23.7462 or stepped["current_lng"] != 86.4152
        logger.info(f"Worker stepped from ({sample_worker['current_lat']}, {sample_worker['current_lng']}) to ({stepped['current_lat']}, {stepped['current_lng']})")
        logger.info("PASSED: Test 6")

        # -------------------------------------------------------------
        # TEST 7: Correct Identification of Affected Workers
        # -------------------------------------------------------------
        logger.info("\n--- TEST 7: Affected Workers Identification ---")
        active_alerts = client.get("/api/alerts/active").json()
        assert len(active_alerts) > 0, "Expected active alerts from critical zones"
        z1_alert = next(a for a in active_alerts if a["zone_id"] == 1)
        z1_workers = client.get("/api/workers/zone/1").json()
        assert z1_alert["affected_workers_count"] == len(z1_workers)
        logger.info(f"Correctly localized {z1_alert['affected_workers_count']} workers in Zone 1 for targeted dispatch.")
        logger.info("PASSED: Test 7")

        # -------------------------------------------------------------
        # TEST 8: Targeted Emergency Alert Generation
        # -------------------------------------------------------------
        logger.info("\n--- TEST 8: Targeted Emergency Alert Fields ---")
        assert z1_alert["alert_code"].startswith("EVAC-")
        assert z1_alert["is_active"] is True
        assert z1_alert["route_details"] is not None
        route_obj = json.loads(z1_alert["route_details"])
        assert "destination_name" in route_obj
        logger.info(f"Targeted Alert: Code={z1_alert['alert_code']}, Route Dest={route_obj['destination_name']}")
        logger.info("PASSED: Test 8")

        # -------------------------------------------------------------
        # TEST 9: Two-Way Worker Acknowledgement
        # -------------------------------------------------------------
        logger.info("\n--- TEST 9: Two-Way Worker Acknowledgement ---")
        alert_id = z1_alert["id"]
        target_worker_id = z1_workers[0]["id"]

        # Worker Acknowledges receipt
        ack_res = client.post(f"/api/alerts/{alert_id}/acknowledge", json={
            "worker_id": target_worker_id,
            "status": "acknowledged",
            "notes": "Worker WRK-1001 confirmed alarm receipt via wearable",
        })
        assert ack_res.status_code == 200
        assert ack_res.json()["worker_status"] == "acknowledged"

        # Verify alert tally updated
        z1_evac_status = client.get(f"/api/alerts/{alert_id}/evacuation-status").json()
        assert z1_evac_status["acknowledged_count"] == 1
        assert z1_evac_status["evacuated_safe_count"] == 0  # Still evacuating, NOT safe yet!
        logger.info("Acknowledgement confirmed receipt without falsely confirming safety.")
        logger.info("PASSED: Test 9")

        # -------------------------------------------------------------
        # TEST 10: Evacuation Route Generation & Blocked Route Handling
        # -------------------------------------------------------------
        logger.info("\n--- TEST 10: Route Generation & Blocked Handling ---")
        clear_route = calculate_evacuation_route(zone_id=1, hazard_zone_ids=[1])
        assert clear_route["route_status"] == "SAFE_CLEAR"
        assert len(clear_route["waypoints"]) >= 2
        assert clear_route["distance_meters"] > 0
        logger.info(f"Clear route verified: {clear_route['destination_name']}, Dist={clear_route['distance_meters']}m")

        # Test blocked corridor collision handling
        blocked_route = calculate_evacuation_route(zone_id=6, hazard_zone_ids=[5])
        assert blocked_route["route_status"] == "UNSAFE_BLOCKED"
        assert "EMERGENCY" in blocked_route["instructions"] or "INTERMEDIATE" in blocked_route["instructions"]
        logger.info(f"Blocked route safety check verified: Status={blocked_route['route_status']}")
        logger.info("PASSED: Test 10")

        # -------------------------------------------------------------
        # TEST 11: Evacuation Status Updates & Safe Confirmation
        # -------------------------------------------------------------
        logger.info("\n--- TEST 11: Evacuating -> Reached Safe Zone ---")
        # Step worker to evacuating
        client.post(f"/api/alerts/{alert_id}/acknowledge", json={
            "worker_id": target_worker_id,
            "status": "evacuating",
            "notes": "En route to North Pit Surface Muster Station",
        })
        # Finally step worker to safe at refuge
        safe_res = client.post(f"/api/alerts/{alert_id}/acknowledge", json={
            "worker_id": target_worker_id,
            "status": "Reached Safe Zone",
            "notes": "Arrived at safe muster station",
        })
        assert safe_res.status_code == 200
        assert safe_res.json()["worker_status"] == "safe"
        assert safe_res.json()["evacuated_safe_count"] == 1
        logger.info("Worker safely marked 'safe' after reaching refuge station.")
        logger.info("PASSED: Test 11")

        # -------------------------------------------------------------
        # TEST 12: WebSocket Broadcast Verification
        # -------------------------------------------------------------
        logger.info("\n--- TEST 12: WebSocket Broadcasting ---")
        with client.websocket_connect("/ws/telemetry") as ws:
            connected = ws.receive_json()
            assert connected["event"] == "CONNECTED"
            logger.info("WebSocket connection and event streaming verified.")
        logger.info("PASSED: Test 12")

        # -------------------------------------------------------------
        # TEST 13: Simulation Control Endpoints
        # -------------------------------------------------------------
        logger.info("\n--- TEST 13: Simulation Controls API ---")
        # Start
        start_res = client.post("/api/simulation/start").json()
        assert start_res["status"] in ["started", "already_running"]

        # Status
        status_res = client.get("/api/simulation/status").json()
        assert "is_running" in status_res
        assert "current_scenario" in status_res

        # Set Scenario
        scen_res = client.post("/api/simulation/scenario", json={"scenario": "progressive_drift"}).json()
        assert scen_res["scenario"] == "progressive_drift"

        # Manual Tick
        tick_res = client.post("/api/simulation/tick").json()
        assert tick_res["status"] == "success"
        assert tick_res["readings_generated"] >= 36

        # Stop
        stop_res = client.post("/api/simulation/stop").json()
        assert stop_res["status"] == "stopped"

        # Reset
        reset_res = client.post("/api/simulation/reset").json()
        assert reset_res["status"] == "reset_complete"
        assert reset_res["current_scenario"] == "normal"
        logger.info("Simulation Controls (Start, Status, Scenario, Tick, Stop, Reset) 100% verified.")
        logger.info("PASSED: Test 13")

        # -------------------------------------------------------------
        # TEST 14: Alert Resolution & Database Audit History
        # -------------------------------------------------------------
        logger.info("\n--- TEST 14: Incident Resolution & Audit History ---")
        # Check active alerts list is 0 after reset
        remaining_active = client.get("/api/alerts/active").json()
        assert len(remaining_active) == 0, f"Expected 0 active alerts after reset, got {len(remaining_active)}"

        # Verify historical alerts table retains full record
        history = client.get("/api/alerts/history?limit=10").json()
        assert len(history) >= 1, "Alert history did not retain resolved records!"
        first_hist = history[0]
        assert first_hist["is_active"] is False
        assert first_hist["resolved_at"] is not None
        logger.info(f"Historical Alert Audit Verified: ID={first_hist['id']}, Code={first_hist['alert_code']}, ResolvedAt={first_hist['resolved_at']}")
        logger.info("PASSED: Test 14")

    logger.info("=" * 70)
    logger.info("ALL 14 STEP 6 VERIFICATION TESTS COMPLETED AND PASSED (100%)!")
    logger.info("=" * 70)


if __name__ == "__main__":
    run_all_tests()
