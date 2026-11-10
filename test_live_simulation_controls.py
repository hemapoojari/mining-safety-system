import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_live_simulation():
    print("Testing Live Simulation Controls via REST...")

    # 1. Start simulation
    res = requests.post(f"{BASE_URL}/api/simulation/start").json()
    print("[1] Simulation Started:", res)
    assert res["status"] in ["started", "already_running"]

    # 2. Let it run for 4 seconds (at least 1 background tick)
    print("Waiting 4 seconds for background tick...")
    time.sleep(4.0)

    # 3. Check status
    status = requests.get(f"{BASE_URL}/api/simulation/status").json()
    print("[2] Simulation Status after background run:", status)
    assert status["is_running"] is True
    assert status["tick_count"] >= 1

    # 4. Inject Open-Pit Hazard Scenario
    scen_res = requests.post(f"{BASE_URL}/api/simulation/scenario", json={"scenario": "open_pit_hazard"}).json()
    print("[3] Scenario Set to open_pit_hazard:", scen_res)
    assert scen_res["scenario"] == "open_pit_hazard"

    # 5. Wait 4 seconds for background cycle to process hazard and trigger emergency alert
    print("Waiting 4 seconds for background hazard detection & alert dispatch...")
    time.sleep(4.0)

    # 6. Check active alerts
    alerts = requests.get(f"{BASE_URL}/api/alerts/active").json()
    print(f"[4] Active Alerts Detected in background loop: {len(alerts)}")
    assert len(alerts) >= 1, "Expected at least 1 active emergency alert after open_pit_hazard scenario"
    alert = alerts[0]
    print(f"    Alert Code: {alert['alert_code']}, Zone: {alert['zone_name']}, Risk: {alert['risk_tier']}")
    assert alert["risk_tier"] == "Critical"
    assert alert["route_details"] is not None

    # 7. Test 2-way Worker Acknowledgement via API
    alert_id = alert["id"]
    evac_status = requests.get(f"{BASE_URL}/api/alerts/{alert_id}/evacuation-status").json()
    print(f"[5] Evacuation Status Roster: {len(evac_status['workers'])} workers affected")
    if len(evac_status["workers"]) > 0:
        first_w = evac_status["workers"][0]
        ack_res = requests.post(f"{BASE_URL}/api/alerts/{alert_id}/acknowledge", json={
            "worker_id": first_w["worker_id"],
            "status": "acknowledged",
            "notes": "Live test: Worker acknowledged evacuation route",
        }).json()
        print(f"    Worker {first_w['worker_code']} Acknowledged:", ack_res["status"])
        assert ack_res["status"] == "success"
        assert ack_res["worker_status"] == "acknowledged"

    # 8. Reset simulation back to nominal
    reset_res = requests.post(f"{BASE_URL}/api/simulation/reset").json()
    print("[6] Simulation Reset Complete:", reset_res)
    assert reset_res["status"] == "reset_complete"

    # 9. Stop simulation background runner
    stop_res = requests.post(f"{BASE_URL}/api/simulation/stop").json()
    print("[7] Simulation Stopped:", stop_res)
    assert stop_res["status"] == "stopped"

    # 10. Confirm 0 active alerts remain
    active_after_reset = requests.get(f"{BASE_URL}/api/alerts/active").json()
    assert len(active_after_reset) == 0
    print("[8] Verified: 0 active alerts remain after reset.")

    print("\n[ALL LIVE SIMULATION CONTROLS TESTED & VERIFIED 100%]")

if __name__ == "__main__":
    test_live_simulation()
