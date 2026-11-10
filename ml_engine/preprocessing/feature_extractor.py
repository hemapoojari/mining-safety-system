"""
Feature Extraction & Rolling Temporal Engineering
Extracts dynamic indices for Open-Pit and Underground mining risk models.
"""
from typing import Dict, Any, List


class MiningFeatureExtractor:
    """Extracts rate-of-change, Graham's ratio, and cumulative precipitation metrics."""

    @staticmethod
    def compute_grahams_ratio(co_ppm: float, o2_percent: float, ambient_o2: float = 20.9) -> float:
        """
        Graham's Ratio = (CO ppm / 10000) / (ambient_O2% - measured_O2%) * 100
        Standard index used in mining to detect underground spontaneous combustion.
        """
        o2_deficiency = max(0.01, ambient_o2 - o2_percent)
        ratio = (co_ppm / 10000.0) / o2_deficiency * 100.0
        return round(ratio, 4)

    @staticmethod
    def compute_displacement_rate(disp_current: float, disp_previous: float, delta_hours: float) -> float:
        """Rate of slope movement in mm/day."""
        if delta_hours <= 0:
            return 0.0
        return round(((disp_current - disp_previous) / delta_hours) * 24.0, 4)
