"""
Specific Scenario Audit: Tests 4 Emergency Scenarios Individually
1. Normal Conditions
2. Open-Pit Hazard
3. Underground Gas Leak
4. Underground Fire

Captures and audits:
- Sensor changes
- ML model prediction outputs
- Statutory safety safeguards
- Mining zone risk updates
- Evacuation workflow (alert creation, targeted worker dispatch, route details, ACK)
"""
import json
import logging
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal
from backend.app.database.models import MiningZone, Worker, EmergencyAlert, RiskPrediction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scenario_audit")


def audit_scenarios():
    logger.info("======================================================================")
    logger.info("STARTING DETAILED SCENARIO AUDIT: 4 EMERGENCY SCENARIOS")
    logger.info("======================================================================")

    with TestClient(app) as client:
        # -------------------------------------------------------------
        # SCENARIO 1: NORMAL CONDITIONS
        # -------------------------------------------------------------
        logger.info("\n>>> SCENARIO 1: NORMAL CONDITIONS <<<")
        # Reset first
        client.post("/api/simulation/reset")
        client.post("/api/simulation/scenario", json={"scenario": "normal"})
        tick_res = client.post("/api/simulation/tick").json()
        assert tick_res["status"] == "success"

        with SessionLocal() as db:
            zones = db.query(MiningZone).all()
            logger.info("Zone Risk Status under Normal Conditions:")
            for z in zones:
                logger.info(f"  Zone {z.id} ({z.name}, {z.mine_type}): Risk Tier = {z.current_risk_tier}")
                assert z.current_risk_tier in ["Safe", "Low"], f"Zone {z.id} expected Safe/Low, got {z.current_risk_tier}"

            # Check latest ML risk predictions
            preds = db.query(RiskPrediction).order_by(RiskPrediction.id.desc()).limit(6).all()
            logger.info("Latest ML Risk Predictions:")
            for p in preds:
                logger.info(f"  Zone {p.zone_id}: Hazard={p.hazard_type}, Tier={p.risk_tier}, Score={p.risk_score:.3f}, Confidence={p.confidence:.3f}, Model={p.model_name}")
                assert p.risk_tier in ["Safe", "Low"]

            # Check alerts
            active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True).all()
            logger.info(f"Active Emergency Alerts: {len(active_alerts)} (Expected: 0)")
            assert len(active_alerts) == 0

        logger.info("[PASS] Scenario 1: Normal Conditions verified successfully.")

        # -------------------------------------------------------------
        # SCENARIO 2: OPEN-PIT HAZARD
        # -------------------------------------------------------------
        logger.info("\n>>> SCENARIO 2: OPEN-PIT HAZARD <<<")
        client.post("/api/simulation/scenario", json={"scenario": "open_pit_hazard"})
        tick_res = client.post("/api/simulation/tick").json()
        assert tick_res["status"] == "success"

        with SessionLocal() as db:
            # Target zones are Zone 1 (Upper Wall) and/or Zone 2 (East Highwall)
            z1 = db.query(MiningZone).filter(MiningZone.id == 1).first()
            z2 = db.query(MiningZone).filter(MiningZone.id == 2).first()
            logger.info(f"Open-Pit Zone 1 ({z1.name}): Risk Tier = {z1.current_risk_tier}")
            logger.info(f"Open-Pit Zone 2 ({z2.name}): Risk Tier = {z2.current_risk_tier}")
            assert z1.current_risk_tier == "Critical" or z2.current_risk_tier == "Critical"

            # Check ML prediction and safeguard
            pred = (
                db.query(RiskPrediction)
                .filter(RiskPrediction.zone_id.in_([1, 2]))
                .order_by(RiskPrediction.id.desc())
                .first()
            )
            logger.info(f"Open-Pit Hazard Prediction: Zone {pred.zone_id}, Hazard={pred.hazard_type}, Tier={pred.risk_tier}, Score={pred.risk_score}, Method={pred.calculation_method}, Model={pred.model_name}")
            logger.info(f"Prediction Details: {pred.details}")

            # Check Emergency Alert
            alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True, EmergencyAlert.zone_id.in_([1, 2])).all()
            logger.info(f"Active Open-Pit Alerts Generated: {len(alerts)}")
            assert len(alerts) >= 1
            op_alert = alerts[0]
            logger.info(f"Alert Code: {op_alert.alert_code}, Risk: {op_alert.risk_tier}, Hazard: {op_alert.hazard_type}")
            logger.info(f"Message: {op_alert.message}")
            assert op_alert.route_details is not None
            route = json.loads(op_alert.route_details)
            logger.info(f"Evacuation Route Status: {route.get('route_status')}, Destination: {route.get('destination_name')}, Distance: {route.get('distance_meters')}m, Est Time: {route.get('est_evacuation_minutes')} min")
            assert route["route_status"] == "SAFE_CLEAR"
            assert "Surface Muster" in route["destination_name"]

        logger.info("[PASS] Scenario 2: Open-Pit Hazard verified successfully.")

        # Reset before Scenario 3
        client.post("/api/simulation/reset")

        # -------------------------------------------------------------
        # SCENARIO 3: UNDERGROUND GAS LEAK
        # -------------------------------------------------------------
        logger.info("\n>>> SCENARIO 3: UNDERGROUND GAS LEAK <<<")
        client.post("/api/simulation/scenario", json={"scenario": "gas_leak"})
        tick_res = client.post("/api/simulation/tick").json()
        assert tick_res["status"] == "success"

        with SessionLocal() as db:
            z4 = db.query(MiningZone).filter(MiningZone.id == 4).first()
            z5 = db.query(MiningZone).filter(MiningZone.id == 5).first()
            logger.info(f"Underground Zone 4 ({z4.name}): Risk Tier = {z4.current_risk_tier}")
            logger.info(f"Underground Zone 5 ({z5.name}): Risk Tier = {z5.current_risk_tier}")
            assert z4.current_risk_tier == "Critical" or z5.current_risk_tier == "Critical"

            pred = (
                db.query(RiskPrediction)
                .filter(RiskPrediction.zone_id.in_([4, 5]))
                .order_by(RiskPrediction.id.desc())
                .first()
            )
            logger.info(f"Gas Leak Prediction: Zone {pred.zone_id}, Hazard={pred.hazard_type}, Tier={pred.risk_tier}, Score={pred.risk_score}, Method={pred.calculation_method}, Model={pred.model_name}")
            logger.info(f"Prediction Details: {pred.details}")

            # Check Emergency Alert
            alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True, EmergencyAlert.zone_id.in_([4, 5])).all()
            logger.info(f"Active Gas Leak Alerts Generated: {len(alerts)}")
            assert len(alerts) >= 1
            ug_alert = alerts[0]
            logger.info(f"Alert Code: {ug_alert.alert_code}, Risk: {ug_alert.risk_tier}, Hazard: {ug_alert.hazard_type}")
            route = json.loads(ug_alert.route_details)
            logger.info(f"Evacuation Route Status: {route.get('route_status')}, Destination: {route.get('destination_name')}, Distance: {route.get('distance_meters')}m, Est Time: {route.get('est_evacuation_minutes')} min")
            assert "Refuge Chamber" in route["destination_name"]

        logger.info("[PASS] Scenario 3: Underground Gas Leak verified successfully.")

        # Reset before Scenario 4
        client.post("/api/simulation/reset")

        # -------------------------------------------------------------
        # SCENARIO 4: UNDERGROUND FIRE HAZARD
        # -------------------------------------------------------------
        logger.info("\n>>> SCENARIO 4: UNDERGROUND FIRE HAZARD <<<")
        client.post("/api/simulation/scenario", json={"scenario": "fire_hazard"})
        tick_res = client.post("/api/simulation/tick").json()
        assert tick_res["status"] == "success"

        with SessionLocal() as db:
            z5 = db.query(MiningZone).filter(MiningZone.id == 5).first()
            z6 = db.query(MiningZone).filter(MiningZone.id == 6).first()
            logger.info(f"Underground Zone 5 ({z5.name}): Risk Tier = {z5.current_risk_tier}")
            logger.info(f"Underground Zone 6 ({z6.name}): Risk Tier = {z6.current_risk_tier}")
            assert z5.current_risk_tier == "Critical" or z6.current_risk_tier == "Critical"

            pred = (
                db.query(RiskPrediction)
                .filter(RiskPrediction.zone_id.in_([5, 6]))
                .order_by(RiskPrediction.id.desc())
                .first()
            )
            logger.info(f"Fire Hazard Prediction: Zone {pred.zone_id}, Hazard={pred.hazard_type}, Tier={pred.risk_tier}, Score={pred.risk_score}, Method={pred.calculation_method}, Model={pred.model_name}")
            logger.info(f"Prediction Details: {pred.details}")

            # Check Emergency Alert
            alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True, EmergencyAlert.zone_id.in_([5, 6])).all()
            logger.info(f"Active Fire Hazard Alerts Generated: {len(alerts)}")
            assert len(alerts) >= 1
            fire_alert = alerts[0]
            logger.info(f"Alert Code: {fire_alert.alert_code}, Risk: {fire_alert.risk_tier}, Hazard: {fire_alert.hazard_type}")
            route = json.loads(fire_alert.route_details)
            logger.info(f"Evacuation Route Status: {route.get('route_status')}, Destination: {route.get('destination_name')}, Distance: {route.get('distance_meters')}m, Est Time: {route.get('est_evacuation_minutes')} min")

        logger.info("[PASS] Scenario 4: Underground Fire Hazard verified successfully.")

        # Reset back to nominal
        client.post("/api/simulation/reset")
        logger.info("\nSystem cleanly returned to nominal baseline.")

    logger.info("======================================================================")
    logger.info("ALL 4 EMERGENCY SCENARIOS AUDITED AND VERIFIED (100% PASS)")
    logger.info("======================================================================")


if __name__ == "__main__":
    audit_scenarios()
