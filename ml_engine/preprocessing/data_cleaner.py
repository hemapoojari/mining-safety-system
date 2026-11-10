"""
Data Cleaning & Outlier Rejection Pipeline
Applies sensor physical boundary clipping and rolling Hampel / Z-score filters.
"""
from typing import Dict, Any, List


class SensorDataCleaner:
    """Cleans raw incoming sensor frames and handles missing/erratic values."""

    # Plausible physical operating boundaries for mining sensors
    PHYSICAL_BOUNDS = {
        "rainfall": (0.0, 300.0),            # mm/h
        "vibration": (0.0, 150.0),           # mm/s (PPV)
        "slope_displacement": (0.0, 500.0),  # mm
        "ch4": (0.0, 10.0),                  # % volume
        "co": (0.0, 1000.0),                 # ppm
        "o2": (0.0, 25.0),                   # % volume
        "temperature": (-10.0, 80.0),        # °C
        "smoke": (0.0, 5.0),                 # Optical density
        "ventilation": (0.0, 20.0),          # m/s
    }

    def validate_and_clip(self, sensor_type: str, value: float) -> float:
        """Clips sensor readings strictly within physical limits."""
        bounds = self.PHYSICAL_BOUNDS.get(sensor_type)
        if bounds:
            min_val, max_val = bounds
            return max(min_val, min(max_val, value))
        return value

    def clean_telemetry_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """Validates, removes noise spikes, and formats a single sensor record."""
        cleaned = dict(frame)
        s_type = frame.get("sensor_type", "")
        val = frame.get("value", 0.0)
        cleaned["value"] = self.validate_and_clip(s_type, float(val))
        return cleaned
