"""
Open-Pit Rockfall Risk Classification Model
Trained Random Forest Classifier evaluating micro-seismic ground vibrations,
bench crack acceleration, and rainfall load.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_PATH = "ml_engine/saved_models/rockfall_risk_model.joblib"
ENCODER_PATH = "ml_engine/saved_models/label_encoder.joblib"

TIER_SCORES = {
    "Safe": 0.05,
    "Low": 0.25,
    "Medium": 0.50,
    "High": 0.75,
    "Critical": 0.95,
}


class RockfallRiskModel:
    """Inference wrapper for the Open-Pit Rockfall Random Forest Model."""

    def __init__(self):
        self.model_name = "OpenPit_Rockfall_RandomForest"
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
        except Exception as e:
            print(f"[RockfallRiskModel] Warning: Could not load model: {e}")

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Accepts sensor dictionary and returns ML prediction for rockfall detachment risk.
        """
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
            confidence = round(float(max(proba)), 4)
        else:
            if vibration >= 24.0 and crack >= 8.0:
                pred_tier = "Critical"
            elif vibration >= 16.0:
                pred_tier = "High"
            elif vibration >= 8.0:
                pred_tier = "Medium"
            elif vibration >= 3.0:
                pred_tier = "Low"
            else:
                pred_tier = "Safe"
            confidence = 0.85
            prob_dict = {pred_tier: 0.85}

        risk_score = TIER_SCORES.get(pred_tier, 0.05)

        return {
            "hazard_type": "rockfall",
            "predicted_tier": pred_tier,
            "confidence": confidence,
            "risk_score": risk_score,
            "probabilities": prob_dict,
            "model_name": self.model_name,
            "features_used": {
                "ground_vibration": vibration,
                "crack_expansion": crack,
                "displacement_rate": disp_rate,
            },
        }
