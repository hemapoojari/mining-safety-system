"""
Synthetic Dataset Generator for Mining Safety Machine Learning
AI/ML-Powered Mining Safety and Worker Evacuation System

Generates physically grounded, balanced synthetic datasets for:
1. Open-Pit Mining Geotechnical Safety (Slope Instability & Rockfall Risk)
2. Underground Mining Atmospheric Safety (Toxic Gas & Fire Hazard Risk)

DOCUMENTED ASSUMPTIONS & DOMAIN CORRELATIONS:
- Open-Pit:
  * Rainfall increases pore-water pressure and soil moisture, drastically accelerating slope displacement.
  * Ground vibration PPV (blast waves or micro-tremors) triggers rockfall and bench crest failure.
  * Crack expansion combined with high displacement velocity (mm/day) signals imminent wall collapse.
- Underground:
  * Methane (CH4) buildup combined with poor ventilation creates severe explosion/asphyxiation risks.
  * Carbon monoxide (CO) rise with oxygen (O2) depletion indicates early smoldering combustion.
  * Graham's Ratio (CO / Delta O2) provides an empirical index for spontaneous combustion.
  * Low airflow velocity (<0.3 m/s) impairs dispersion and compounds toxic gas concentration.

NOTICE: Synthetic datasets are generated for algorithmic validation and prototype demonstration;
they do not substitute for empirical geotechnical testing in live mines.
"""
import os
import numpy as np
import pandas as pd

# Standard 5-tier classification labels
RISK_TIERS = ["Safe", "Low", "Medium", "High", "Critical"]


def generate_open_pit_dataset(n_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates balanced open-pit dataset containing:
    - rainfall_intensity (mm/h): [0, 100]
    - ground_vibration (mm/s PPV): [0, 50]
    - slope_displacement (mm): [0, 25]
    - crack_expansion (mm): [0, 18]
    - soil_moisture (%): [15, 95]
    - displacement_rate (mm/day): [0, 45]
    """
    np.random.seed(random_state)
    samples_per_class = n_samples // 5

    data_rows = []

    for tier_idx, tier_name in enumerate(RISK_TIERS):
        for _ in range(samples_per_class):
            if tier_name == "Safe":
                rainfall = np.random.uniform(0.0, 8.0)
                vibration = np.random.uniform(0.1, 4.0)
                displacement = np.random.uniform(0.0, 1.2)
                crack = np.random.uniform(0.0, 0.8)
                moisture = np.random.uniform(15.0, 45.0)
                disp_rate = np.random.uniform(0.0, 1.5)
            elif tier_name == "Low":
                rainfall = np.random.uniform(5.0, 18.0)
                vibration = np.random.uniform(3.0, 9.0)
                displacement = np.random.uniform(1.0, 3.5)
                crack = np.random.uniform(0.5, 2.5)
                moisture = np.random.uniform(35.0, 60.0)
                disp_rate = np.random.uniform(1.0, 4.0)
            elif tier_name == "Medium":
                rainfall = np.random.uniform(15.0, 32.0)
                vibration = np.random.uniform(8.0, 16.0)
                displacement = np.random.uniform(3.0, 7.0)
                crack = np.random.uniform(2.0, 5.5)
                moisture = np.random.uniform(50.0, 75.0)
                disp_rate = np.random.uniform(3.5, 9.0)
            elif tier_name == "High":
                rainfall = np.random.uniform(28.0, 55.0)
                vibration = np.random.uniform(14.0, 25.0)
                displacement = np.random.uniform(6.5, 13.0)
                crack = np.random.uniform(5.0, 10.0)
                moisture = np.random.uniform(65.0, 88.0)
                disp_rate = np.random.uniform(8.0, 18.0)
            else:  # Critical
                rainfall = np.random.uniform(45.0, 110.0)
                vibration = np.random.uniform(22.0, 55.0)
                displacement = np.random.uniform(12.0, 28.0)
                crack = np.random.uniform(9.0, 19.0)
                moisture = np.random.uniform(80.0, 98.0)
                disp_rate = np.random.uniform(16.0, 48.0)

            # Add natural geological measurement noise
            rainfall += np.random.normal(0, 0.5)
            vibration += np.random.normal(0, 0.2)
            displacement += np.random.normal(0, 0.1)
            crack += np.random.normal(0, 0.1)
            moisture += np.random.normal(0, 0.5)
            disp_rate += np.random.normal(0, 0.2)

            # Clip within physical reality
            rainfall = max(0.0, rainfall)
            vibration = max(0.0, vibration)
            displacement = max(0.0, displacement)
            crack = max(0.0, crack)
            moisture = min(100.0, max(10.0, moisture))
            disp_rate = max(0.0, disp_rate)

            # Rockfall risk logic: heavy vibration + crack expansion + steep slope triggers rock detachment
            rockfall_score = 0.55 * (vibration / 30.0) + 0.35 * (crack / 12.0) + 0.10 * (rainfall / 60.0)
            if rockfall_score >= 0.80 or (vibration > 24.0 and crack > 8.0):
                rockfall_tier = "Critical"
            elif rockfall_score >= 0.60 or vibration > 16.0:
                rockfall_tier = "High"
            elif rockfall_score >= 0.35:
                rockfall_tier = "Medium"
            elif rockfall_score >= 0.15:
                rockfall_tier = "Low"
            else:
                rockfall_tier = "Safe"

            data_rows.append({
                "rainfall_intensity": round(rainfall, 2),
                "ground_vibration": round(vibration, 2),
                "slope_displacement": round(displacement, 2),
                "crack_expansion": round(crack, 2),
                "soil_moisture": round(moisture, 2),
                "displacement_rate": round(disp_rate, 2),
                "slope_risk": tier_name,
                "rockfall_risk": rockfall_tier,
            })

    df = pd.DataFrame(data_rows).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


def generate_underground_dataset(n_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates balanced underground mining dataset containing:
    - methane_ch4 (% vol): [0, 4.5]
    - carbon_monoxide_co (ppm): [0, 220]
    - oxygen_o2 (% vol): [14, 21]
    - temperature (°C): [18, 65]
    - smoke_density (OD): [0, 2.5]
    - ventilation_velocity (m/s): [0.05, 4.0]
    """
    np.random.seed(random_state)
    samples_per_class = n_samples // 5

    data_rows = []

    for tier_idx, tier_name in enumerate(RISK_TIERS):
        for _ in range(samples_per_class):
            if tier_name == "Safe":
                ch4 = np.random.uniform(0.02, 0.35)
                co = np.random.uniform(1.0, 9.0)
                o2 = np.random.uniform(20.6, 20.95)
                temp = np.random.uniform(20.0, 27.0)
                smoke = np.random.uniform(0.005, 0.06)
                vent = np.random.uniform(1.2, 3.2)
            elif tier_name == "Low":
                ch4 = np.random.uniform(0.30, 0.70)
                co = np.random.uniform(8.0, 19.0)
                o2 = np.random.uniform(19.8, 20.6)
                temp = np.random.uniform(26.0, 32.0)
                smoke = np.random.uniform(0.05, 0.18)
                vent = np.random.uniform(0.9, 2.2)
            elif tier_name == "Medium":
                ch4 = np.random.uniform(0.65, 1.10)
                co = np.random.uniform(18.0, 34.0)
                o2 = np.random.uniform(18.8, 19.8)
                temp = np.random.uniform(31.0, 39.0)
                smoke = np.random.uniform(0.15, 0.38)
                vent = np.random.uniform(0.6, 1.4)
            elif tier_name == "High":
                ch4 = np.random.uniform(1.05, 1.80)
                co = np.random.uniform(32.0, 65.0)
                o2 = np.random.uniform(17.5, 18.9)
                temp = np.random.uniform(38.0, 48.0)
                smoke = np.random.uniform(0.35, 0.75)
                vent = np.random.uniform(0.25, 0.75)
            else:  # Critical
                ch4 = np.random.uniform(1.50, 4.20)
                co = np.random.uniform(55.0, 210.0)
                o2 = np.random.uniform(14.5, 17.5)
                temp = np.random.uniform(46.0, 68.0)
                smoke = np.random.uniform(0.70, 2.20)
                vent = np.random.uniform(0.05, 0.35)

            # Add sensor measurement noise
            ch4 += np.random.normal(0, 0.02)
            co += np.random.normal(0, 0.5)
            o2 += np.random.normal(0, 0.05)
            temp += np.random.normal(0, 0.3)
            smoke += np.random.normal(0, 0.01)
            vent += np.random.normal(0, 0.03)

            # Physical clipping
            ch4 = max(0.0, ch4)
            co = max(0.0, co)
            o2 = min(21.0, max(14.0, o2))
            temp = max(15.0, temp)
            smoke = max(0.0, smoke)
            vent = max(0.05, vent)

            # Fire hazard logic: high temperature + smoke + CO rise
            o2_deficit = max(0.01, 20.9 - o2)
            grahams = (co / 10000.0) / o2_deficit * 100.0
            fire_score = 0.40 * min(1.0, (temp - 25.0) / 25.0) + 0.35 * min(1.0, smoke / 0.8) + 0.25 * min(1.0, grahams / 2.0)
            
            if fire_score >= 0.80 or temp > 50.0 or smoke > 0.8:
                fire_tier = "Critical"
            elif fire_score >= 0.60 or temp > 38.0 or smoke > 0.4:
                fire_tier = "High"
            elif fire_score >= 0.35 or temp > 32.0:
                fire_tier = "Medium"
            elif fire_score >= 0.15:
                fire_tier = "Low"
            else:
                fire_tier = "Safe"

            data_rows.append({
                "methane_ch4": round(ch4, 3),
                "carbon_monoxide_co": round(co, 1),
                "oxygen_o2": round(o2, 2),
                "temperature": round(temp, 1),
                "smoke_density": round(smoke, 3),
                "ventilation_velocity": round(vent, 2),
                "gas_risk": tier_name,
                "fire_risk": fire_tier,
            })

    df = pd.DataFrame(data_rows).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


def generate_and_save_all_datasets():
    """Generates and writes CSV files to ml_engine/datasets/."""
    os.makedirs("ml_engine/datasets", exist_ok=True)

    print("Generating Open-Pit mining dataset (5,000 samples)...")
    df_op = generate_open_pit_dataset(n_samples=5000)
    op_path = "ml_engine/datasets/open_pit_dataset.csv"
    df_op.to_csv(op_path, index=False)
    print(f"Saved: {op_path} (Shape: {df_op.shape})")

    print("Generating Underground mining dataset (5,000 samples)...")
    df_ug = generate_underground_dataset(n_samples=5000)
    ug_path = "ml_engine/datasets/underground_dataset.csv"
    df_ug.to_csv(ug_path, index=False)
    print(f"Saved: {ug_path} (Shape: {df_ug.shape})")

    return df_op, df_ug


if __name__ == "__main__":
    generate_and_save_all_datasets()
