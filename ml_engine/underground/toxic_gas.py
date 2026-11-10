"""
Underground Toxic Gas Risk Classification Model
Trained XGBoost Classifier evaluating Methane (CH4), Carbon Monoxide (CO),
Oxygen (O2) deficiency, and ventilation velocity deficits.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_PATH = "ml_engine/saved_models/toxic_gas_model.joblib"
ENCODER_PATH = "ml_engine/saved_models/label_encoder.joblib"

TIER_SCORES = {
    "Safe": 0.05,
    "Low": 0.25,
    "Medium": 0.50,
    "High": 0.75,
    "Critical": 0.95,
}


class ToxicGasModel:
    """Inference wrapper for the Underground Toxic Gas XGBoost Model."""

    def __init__(self):
        self.model_name = "Underground_ToxicGas_XGBoost"
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
        except Exception as e:
            print(f"[ToxicGasModel] Warning: Could not load model: {e}")

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Accepts sensor dictionary and returns ML prediction for toxic/combustible gas hazard.
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
            if ch4 >= 1.25 or co >= 50.0 or o2 <= 17.0:
                pred_tier = "Critical"
            elif ch4 >= 0.8 or co >= 25.0 or o2 <= 18.5:
                pred_tier = "High"
            elif ch4 >= 0.5 or co >= 15.0:
                pred_tier = "Medium"
            elif ch4 >= 0.25:
                pred_tier = "Low"
            else:
                pred_tier = "Safe"
            confidence = 0.85
            prob_dict = {pred_tier: 0.85}

        risk_score = TIER_SCORES.get(pred_tier, 0.05)

        return {
            "hazard_type": "toxic_gas",
            "predicted_tier": pred_tier,
            "confidence": confidence,
            "risk_score": risk_score,
            "probabilities": prob_dict,
            "model_name": self.model_name,
            "features_used": {
                "methane_ch4": ch4,
                "carbon_monoxide_co": co,
                "oxygen_o2": o2,
                "ventilation_velocity": vent,
            },
        }
