"""
Centralized AI/ML Risk Assessment & Multi-Hazard Fusion Service
AI/ML-Powered Mining Safety and Worker Evacuation System

Integrates trained Machine Learning models with statutory threshold safeguards:
- Open-Pit:
  * Slope Instability Model (XGBoost Classifier)
  * Rockfall Risk Model (Random Forest Classifier)
  * Geotechnical Threshold Safeguards
- Underground:
  * Toxic Gas Risk Model (XGBoost Classifier)
  * Fire Hazard & Thermal Model (Random Forest Classifier)
  * Atmospheric Safety Safeguards

DEFENSE-IN-DEPTH ARCHITECTURE:
1. Machine learning models detect subtle multi-feature combinatorial anomalies *before* any
   single sensor exceeds statutory limits.
2. Independent statutory physical thresholds (DGMS/USBM/OSHA) act as a failsafe; if an extreme
   event occurs (e.g., CH4 >= 1.25% or displacement >= 12mm), the system guarantees immediate
   escalation to Critical regardless of model smoothing.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from ml_engine.open_pit.slope_stability import SlopeStabilityModel
from ml_engine.open_pit.rockfall_risk import RockfallRiskModel
from ml_engine.underground.toxic_gas import ToxicGasModel
from ml_engine.underground.fire_hazard import FireHazardModel

logger = logging.getLogger("mining_safety.risk_engine")


class RiskTier:
    SAFE = "Safe"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


TIER_ORDER = {
    RiskTier.SAFE: 1,
    RiskTier.LOW: 2,
    RiskTier.MEDIUM: 3,
    RiskTier.HIGH: 4,
    RiskTier.CRITICAL: 5,
}

ORDER_TO_TIER = {v: k for k, v in TIER_ORDER.items()}

# Initialize singleton ML model instances
_slope_model = SlopeStabilityModel()
_rockfall_model = RockfallRiskModel()
_toxic_gas_model = ToxicGasModel()
_fire_model = FireHazardModel()


def score_to_risk_tier(score: float) -> str:
    """Map a normalized hazard score [0.0, 1.0] to a standardized 5-tier classification."""
    if score >= 0.80:
        return RiskTier.CRITICAL
    elif score >= 0.60:
        return RiskTier.HIGH
    elif score >= 0.35:
        return RiskTier.MEDIUM
    elif score >= 0.15:
        return RiskTier.LOW
    return RiskTier.SAFE


# ---------------------------------------------------------
# OPEN-PIT THRESHOLD SAFEGUARD LOGIC
# ---------------------------------------------------------

def evaluate_open_pit_safeguard(readings: Dict[str, float]) -> Dict[str, Any]:
    """Physical statutory threshold check for open-pit mining."""
    rainfall = readings.get("rainfall", readings.get("rainfall_intensity", 0.0))
    vibration = readings.get("vibration", readings.get("ground_vibration", 0.0))
    displacement = readings.get("slope_displacement", 0.0)

    rain_score = min(1.0, max(0.0, rainfall / 60.0))
    vib_score = min(1.0, max(0.0, vibration / 25.0))
    disp_score = min(1.0, max(0.0, displacement / 15.0))

    composite = round(0.45 * disp_score + 0.30 * vib_score + 0.25 * rain_score, 4)

    # Statutory safety triggers
    if displacement >= 12.0 or vibration >= 22.0 or rainfall >= 55.0:
        composite = max(composite, 0.85)
    elif displacement >= 6.0 or vibration >= 14.0 or rainfall >= 35.0:
        composite = max(composite, 0.65)

    dominant = "slope_displacement"
    if vib_score > disp_score and vib_score > rain_score:
        dominant = "ground_vibration"
    elif rain_score > disp_score and rain_score > vib_score:
        dominant = "heavy_rainfall"

    return {
        "composite_score": composite,
        "risk_tier": score_to_risk_tier(composite),
        "dominant_hazard": dominant,
        "breakdown": {
            "rainfall_mm_h": rainfall,
            "vibration_ppv_mm_s": vibration,
            "slope_displacement_mm": displacement,
        },
    }


# ---------------------------------------------------------
# UNDERGROUND THRESHOLD SAFEGUARD LOGIC
# ---------------------------------------------------------

def evaluate_underground_safeguard(readings: Dict[str, float]) -> Dict[str, Any]:
    """Physical statutory threshold check for underground mining."""
    ch4 = readings.get("ch4", readings.get("methane_ch4", 0.0))
    co = readings.get("co", readings.get("carbon_monoxide_co", 0.0))
    o2 = readings.get("o2", readings.get("oxygen_o2", 20.9))
    temp = readings.get("temperature", 24.0)
    smoke = readings.get("smoke", readings.get("smoke_density", 0.0))
    vent = readings.get("ventilation", readings.get("ventilation_velocity", 1.5))

    ch4_score = min(1.0, max(0.0, ch4 / 1.25))
    co_score = min(1.0, max(0.0, co / 50.0))
    o2_deficit_score = min(1.0, max(0.0, (19.5 - o2) / 3.5)) if o2 < 19.5 else 0.0
    temp_score = min(1.0, max(0.0, (temp - 30.0) / 25.0)) if temp > 30.0 else 0.0
    smoke_score = min(1.0, max(0.0, smoke / 0.8))

    o2_deficit = max(0.01, 20.9 - o2)
    grahams_ratio = round((co / 10000.0) / o2_deficit * 100.0, 3)
    grahams_score = min(1.0, max(0.0, grahams_ratio / 1.5))

    vent_multiplier = 1.3 if vent < 0.3 else (1.15 if vent < 0.6 else 1.0)
    gas_risk = max(ch4_score, co_score, o2_deficit_score)
    fire_risk = max(temp_score * 0.4 + smoke_score * 0.3 + grahams_score * 0.3, smoke_score)

    composite = round(min(1.0, max(gas_risk, fire_risk) * vent_multiplier), 4)

    # Statutory safety triggers
    if ch4 >= 1.25 or co >= 50.0 or o2 <= 17.0 or temp >= 50.0 or smoke >= 0.7:
        composite = max(composite, 0.85)
    elif ch4 >= 0.8 or co >= 25.0 or o2 <= 18.5 or temp >= 38.0 or smoke >= 0.4:
        composite = max(composite, 0.65)

    dominant = "toxic_gas"
    if fire_risk > gas_risk:
        dominant = "fire_hazard"
    elif ch4_score > co_score and ch4_score > o2_deficit_score:
        dominant = "combustible_methane"
    elif o2_deficit_score > co_score:
        dominant = "oxygen_depletion"

    return {
        "composite_score": composite,
        "risk_tier": score_to_risk_tier(composite),
        "dominant_hazard": dominant,
        "breakdown": {
            "ch4_percent": ch4,
            "co_ppm": co,
            "o2_percent": o2,
            "temperature_celsius": temp,
            "smoke_optical_density": smoke,
            "ventilation_velocity_m_s": vent,
            "grahams_ratio": grahams_ratio,
        },
    }


# ---------------------------------------------------------
# UNIFIED CENTRAL DISPATCHER WITH ML INTEGRATION
# ---------------------------------------------------------

def assess_zone_risk(mine_type: str, readings: Dict[str, float]) -> Dict[str, Any]:
    """
    Central Risk Assessment Engine.
    Executes dedicated ML models for the specified mine type and merges with
    independent statutory physical threshold safeguards (Defense-in-Depth).
    """
    if mine_type == "open_pit":
        # 1. Run Open-Pit Machine Learning Models
        slope_pred = _slope_model.predict(readings)
        rockfall_pred = _rockfall_model.predict(readings)

        # 2. Run Open-Pit Statutory Physical Threshold Safeguard
        safeguard = evaluate_open_pit_safeguard(readings)

        # Select most severe ML hazard
        slope_order = TIER_ORDER.get(slope_pred["predicted_tier"], 1)
        rockfall_order = TIER_ORDER.get(rockfall_pred["predicted_tier"], 1)

        if slope_order >= rockfall_order:
            top_ml_pred = slope_pred
            ml_dominant = "slope_instability"
        else:
            top_ml_pred = rockfall_pred
            ml_dominant = "rockfall"

        top_ml_order = max(slope_order, rockfall_order)
        safeguard_order = TIER_ORDER.get(safeguard["risk_tier"], 1)

        # Final unified tier is the maximum of ML prediction and physical statutory threshold
        final_order = max(top_ml_order, safeguard_order)
        final_tier = ORDER_TO_TIER[final_order]

        composite_score = max(top_ml_pred["risk_score"], safeguard["composite_score"])
        dominant_hazard = ml_dominant if top_ml_order >= safeguard_order else safeguard["dominant_hazard"]
        winning_model = top_ml_pred["model_name"]
        confidence = top_ml_pred["confidence"]

        return {
            "mine_type": "open_pit",
            "risk_tier": final_tier,
            "composite_score": round(float(composite_score), 4),
            "dominant_hazard": dominant_hazard,
            "model_name": winning_model,
            "confidence": confidence,
            "calculation_method": "ml_xgboost_rf_with_statutory_safeguard",
            "ml_predictions": {
                "slope_instability": slope_pred,
                "rockfall": rockfall_pred,
            },
            "safeguard_evaluation": safeguard,
            "breakdown": {
                **safeguard["breakdown"],
                "ml_dominant": ml_dominant,
                "ml_tier": top_ml_pred["predicted_tier"],
                "confidence": confidence,
            },
        }

    else:
        # 1. Run Underground Machine Learning Models
        gas_pred = _toxic_gas_model.predict(readings)
        fire_pred = _fire_model.predict(readings)

        # 2. Run Underground Statutory Physical Threshold Safeguard
        safeguard = evaluate_underground_safeguard(readings)

        # Select most severe ML hazard
        gas_order = TIER_ORDER.get(gas_pred["predicted_tier"], 1)
        fire_order = TIER_ORDER.get(fire_pred["predicted_tier"], 1)

        if gas_order >= fire_order:
            top_ml_pred = gas_pred
            ml_dominant = "toxic_gas"
        else:
            top_ml_pred = fire_pred
            ml_dominant = "fire_hazard"

        top_ml_order = max(gas_order, fire_order)
        safeguard_order = TIER_ORDER.get(safeguard["risk_tier"], 1)

        final_order = max(top_ml_order, safeguard_order)
        final_tier = ORDER_TO_TIER[final_order]

        composite_score = max(top_ml_pred["risk_score"], safeguard["composite_score"])
        dominant_hazard = ml_dominant if top_ml_order >= safeguard_order else safeguard["dominant_hazard"]
        winning_model = top_ml_pred["model_name"]
        confidence = top_ml_pred["confidence"]

        return {
            "mine_type": "underground",
            "risk_tier": final_tier,
            "composite_score": round(float(composite_score), 4),
            "dominant_hazard": dominant_hazard,
            "model_name": winning_model,
            "confidence": confidence,
            "calculation_method": "ml_xgboost_rf_with_statutory_safeguard",
            "ml_predictions": {
                "toxic_gas": gas_pred,
                "fire_hazard": fire_pred,
            },
            "safeguard_evaluation": safeguard,
            "breakdown": {
                **safeguard["breakdown"],
                "ml_dominant": ml_dominant,
                "ml_tier": top_ml_pred["predicted_tier"],
                "confidence": confidence,
            },
        }
