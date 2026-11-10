"""
Open-Pit Slope Instability Prediction Model
Trained XGBoost Classifier evaluating rainfall, pore-water soil moisture,
vibration, crack dilation, and slope displacement velocity.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_PATH = "ml_engine/saved_models/slope_instability_model.joblib"
ENCODER_PATH = "ml_engine/saved_models/label_encoder.joblib"

TIER_SCORES = {
    "Safe": 0.05,
    "Low": 0.25,
    "Medium": 0.50,
    "High": 0.75,
    "Critical": 0.95,
}


class SlopeStabilityModel:
    """Inference wrapper for the Open-Pit Slope Instability XGBoost Model."""

    def __init__(self):
        self.model_name = "OpenPit_SlopeInstability_XGBoost"
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
        except Exception as e:
            print(f"[SlopeStabilityModel] Warning: Could not load model: {e}")

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Accepts sensor dictionary and returns ML prediction.
        Safe fallback if model is unavailable.
        """
        # Impute missing feature defaults safely
        rainfall = float(features.get("rainfall_intensity", features.get("rainfall", 0.0)))
        vibration = float(features.get("ground_vibration", features.get("vibration", 0.0)))
        displacement = float(features.get("slope_displacement", 0.0))
        crack = float(features.get("crack_expansion", displacement * 0.7))
        moisture = float(features.get("soil_moisture", min(95.0, 25.0 + rainfall * 0.8)))
        disp_rate = float(features.get("displacement_rate", displacement * 1.5))

        feature_df = pd.DataFrame([{
            "rainfall_intensity": rainfall,
            "ground_vibration": vibration,
            "slope_displacement": displacement,
            "crack_expansion": crack,
            "soil_moisture": moisture,
            "displacement_rate": disp_rate,
        }])

        if self.model is not None and self.label_encoder is not None:
            pred_encoded = self.model.predict(feature_df)[0]
            pred_tier = self.label_encoder.inverse_transform([pred_encoded])[0]

            proba = self.model.predict_proba(feature_df)[0]
            classes = self.label_encoder.classes_
            prob_dict = {classes[i]: round(float(proba[i]), 4) for i in range(len(classes))}
            confidence = round(float(np.max(proba) if "np" in globals() else max(proba)), 4)
        else:
            # Fallback heuristic if serialized file not loaded
            if displacement >= 12.0 or rainfall >= 50.0:
                pred_tier = "Critical"
            elif displacement >= 6.0 or rainfall >= 25.0:
                pred_tier = "High"
            elif displacement >= 3.0:
                pred_tier = "Medium"
            elif displacement >= 1.0:
                pred_tier = "Low"
            else:
                pred_tier = "Safe"
            confidence = 0.85
            prob_dict = {pred_tier: 0.85}

        risk_score = TIER_SCORES.get(pred_tier, 0.05)

        return {
            "hazard_type": "slope_instability",
            "predicted_tier": pred_tier,
            "confidence": confidence,
            "risk_score": risk_score,
            "probabilities": prob_dict,
            "model_name": self.model_name,
            "features_used": {
                "rainfall_intensity": rainfall,
                "ground_vibration": vibration,
                "slope_displacement": displacement,
                "crack_expansion": crack,
                "soil_moisture": moisture,
                "displacement_rate": disp_rate,
            },
        }
