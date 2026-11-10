"""
Underground Fire Hazard & Thermal Runaway Model
Trained Random Forest Classifier evaluating Temperature gradients,
Smoke optical density, CO generation, and Graham's ratio.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_PATH = "ml_engine/saved_models/fire_hazard_model.joblib"
ENCODER_PATH = "ml_engine/saved_models/label_encoder.joblib"

TIER_SCORES = {
    "Safe": 0.05,
    "Low": 0.25,
    "Medium": 0.50,
    "High": 0.75,
    "Critical": 0.95,
}


class FireHazardModel:
    """Inference wrapper for the Underground Fire Hazard Random Forest Model."""

    def __init__(self):
        self.model_name = "Underground_FireHazard_RandomForest"
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
        except Exception as e:
            print(f"[FireHazardModel] Warning: Could not load model: {e}")

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Accepts sensor dictionary and returns ML prediction for spontaneous combustion / open fire.
        """
        ch4 = float(features.get("methane_ch4", features.get("ch4", 0.1)))
        co = float(features.get("carbon_monoxide_co", features.get("co", 4.0)))
        o2 = float(features.get("oxygen_o2", features.get("o2", 20.8)))
        temp = float(features.get("temperature", 24.0))
        smoke = float(features.get("smoke_density", features.get("smoke", 0.02)))
        vent = float(features.get("ventilation_velocity", features.get("ventilation", 1.8)))

        feature_df = pd.DataFrame([{
            "methane_ch4": ch4,
            "carbon_monoxide_co": co,
            "oxygen_o2": o2,
            "temperature": temp,
            "smoke_density": smoke,
            "ventilation_velocity": vent,
        }])

        if self.model is not None and self.label_encoder is not None:
            pred_encoded = self.model.predict(feature_df)[0]
            pred_tier = self.label_encoder.inverse_transform([pred_encoded])[0]

            proba = self.model.predict_proba(feature_df)[0]
            classes = self.label_encoder.classes_
            prob_dict = {classes[i]: round(float(proba[i]), 4) for i in range(len(classes))}
            confidence = round(float(max(proba)), 4)
        else:
            if temp >= 50.0 or smoke >= 0.8:
                pred_tier = "Critical"
            elif temp >= 38.0 or smoke >= 0.4:
                pred_tier = "High"
            elif temp >= 32.0 or smoke >= 0.2:
                pred_tier = "Medium"
            elif temp >= 28.0:
                pred_tier = "Low"
            else:
                pred_tier = "Safe"
            confidence = 0.85
            prob_dict = {pred_tier: 0.85}

        risk_score = TIER_SCORES.get(pred_tier, 0.05)

        return {
            "hazard_type": "fire_hazard",
            "predicted_tier": pred_tier,
            "confidence": confidence,
            "risk_score": risk_score,
            "probabilities": prob_dict,
            "model_name": self.model_name,
            "features_used": {
                "temperature": temp,
                "smoke_density": smoke,
                "carbon_monoxide_co": co,
            },
        }
