"""
Advanced Real-Time Synthetic Sensor Data Generator
Simulates high-frequency geotechnical & atmospheric sensor telemetry streams
for Open-Pit and Underground mining modules.

Features:
- Realistic baselines with diurnal drift and sensor noise
- Progressive hazard development (creep stages, gradual gas accumulation)
- Sudden emergency scenarios (methane surge, underground fire, slope failure)
- 6 Open-pit sensors: rainfall, vibration, slope_displacement, crack_expansion, soil_moisture, displacement_rate
- 6 Underground sensors: ch4, co, o2, temperature, smoke, ventilation
- Unique sensor codes and zone mappings
- Simulation controls: start, stop, reset, set_scenario
"""
import math
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class SensorSimulator:
    """
    Simulates multi-parameter continuous mining sensor networks
    with realistic physical correlations, drift, and hazard injection.
    """

    def __init__(self):
        self.is_running = True
        self.current_scenario = "normal"  # normal, progressive_drift, open_pit_hazard, gas_leak, fire_hazard
        self.tick_count = 0
        self.scenario_tick = 0

        # Base physical state tracking per zone to enable progressive drift
        self._zone_states: Dict[int, Dict[str, float]] = {}
        self._init_zone_baselines()

    def _init_zone_baselines(self):
        """Initializes nominal baseline parameters for all 6 zones (3 open-pit, 3 underground)."""
        # Open-pit zones (1, 2, 3)
        for zid in [1, 2, 3]:
            self._zone_states[zid] = {
                "rainfall": 1.2,          # mm/h
                "vibration": 0.45,        # mm/s
                "slope_displacement": 0.15, # mm
                "crack_expansion": 0.08,  # mm
                "soil_moisture": 22.0,    # %
                "displacement_rate": 0.25, # mm/day
            }

        # Underground zones (4, 5, 6)
        for zid in [4, 5, 6]:
            self._zone_states[zid] = {
                "ch4": 0.12,              # %
                "co": 4.5,               # ppm
                "o2": 20.8,              # %
                "temperature": 23.5,     # °C
                "smoke": 0.02,           # OD/m
                "ventilation": 1.85,     # m/s
            }

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def reset(self):
        self.current_scenario = "normal"
        self.tick_count = 0
        self.scenario_tick = 0
        self._init_zone_baselines()

    def set_scenario(self, scenario: str):
        """
        Sets active simulation scenario:
        - 'normal': Nominal steady-state baseline
        - 'progressive_drift': Slowly accumulating strain and gas levels
        - 'open_pit_hazard': Severe slope displacement, crack expansion & vibration
        - 'gas_leak': Methane outburst and ventilation breakdown in underground drift
        - 'fire_hazard': Thermal runaway, dense smoke and toxic carbon monoxide
        """
        valid = ["normal", "progressive_drift", "open_pit_hazard", "gas_leak", "fire_hazard"]
        if scenario not in valid:
            raise ValueError(f"Invalid scenario '{scenario}'. Valid options: {valid}")
        self.current_scenario = scenario
        self.scenario_tick = 0

    def trigger_anomaly(self, anomaly_type: str):
        """Backward-compatible mapping for existing endpoints."""
        mapping = {
            "rockfall": "open_pit_hazard",
            "gas_leak": "gas_leak",
            "thermal_runaway": "fire_hazard",
            "normal": "normal",
        }
        self.set_scenario(mapping.get(anomaly_type, anomaly_type))

    def step(self):
        """Advances simulation by one tick, updating progressive drift state."""
        self.tick_count += 1
        self.scenario_tick += 1

    def generate_open_pit_reading(self, zone_id: int) -> List[Dict[str, Any]]:
        """
        Generates 6 geotechnical & hydrometeorological sensor readings for an Open-Pit zone.
        Injected hazard targets Zone 1 (Upper Wall) or Zone 2 (Highwall).
        """
        now = datetime.now(timezone.utc)
        state = self._zone_states.get(zone_id, {
            "rainfall": 1.0, "vibration": 0.5, "slope_displacement": 0.2,
            "crack_expansion": 0.1, "soil_moisture": 20.0, "displacement_rate": 0.3
        })

        is_target_zone = (zone_id in [1, 2])
        is_hazard = (self.current_scenario == "open_pit_hazard" and is_target_zone)
        is_drift = (self.current_scenario == "progressive_drift" and is_target_zone)

        # Baseline diurnal drift + Gaussian noise
        noise = lambda s: random.gauss(0, s)

        if is_hazard:
            # Sudden catastrophic kinematic failure scenario
            rainfall = min(120.0, max(45.0, 75.0 + noise(10.0)))
            vibration = min(60.0, max(22.0, 35.0 + noise(6.0)))
            slope_disp = min(40.0, max(14.0, 22.0 + noise(3.0)))
            crack_exp = min(30.0, max(12.0, 18.0 + noise(2.5)))
            soil_moist = min(98.0, max(75.0, 88.0 + noise(4.0)))
            disp_rate = min(50.0, max(18.0, 32.0 + noise(5.0)))
            status = "critical"
        elif is_drift:
            # Progressive creep acceleration
            factor = min(3.0, 1.0 + (self.scenario_tick * 0.15))
            rainfall = max(0.0, state["rainfall"] * factor + noise(1.0))
            vibration = max(0.1, state["vibration"] * factor + noise(0.2))
            slope_disp = max(0.1, state["slope_displacement"] * factor + noise(0.3))
            crack_exp = max(0.05, state["crack_expansion"] * factor + noise(0.2))
            soil_moist = min(95.0, state["soil_moisture"] + (self.scenario_tick * 2.5))
            disp_rate = max(0.2, state["displacement_rate"] * factor + noise(0.4))
            status = "warning" if factor > 1.8 else "active"
        else:
            # Nominal steady state
            rainfall = max(0.0, state["rainfall"] + noise(0.3))
            vibration = max(0.05, state["vibration"] + noise(0.08))
            slope_disp = max(0.02, state["slope_displacement"] + noise(0.02))
            crack_exp = max(0.01, state["crack_expansion"] + noise(0.01))
            soil_moist = max(10.0, min(45.0, state["soil_moisture"] + noise(0.5)))
            disp_rate = max(0.05, state["displacement_rate"] + noise(0.05))
            status = "active"

        return [
            {
                "sensor_code": f"RAIN_Z{zone_id}",
                "name": f"Precipitation Gauge Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "rainfall",
                "value": round(rainfall, 2),
                "unit": "mm/h",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"VIB_Z{zone_id}",
                "name": f"Seismic Tri-Axial Accelerometer Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "vibration",
                "value": round(vibration, 2),
                "unit": "mm/s",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"SLOPE_Z{zone_id}",
                "name": f"Multipoint Borehole Extensometer Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "slope_displacement",
                "value": round(slope_disp, 2),
                "unit": "mm",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"CRACK_Z{zone_id}",
                "name": f"Joint Crackmeter Gauge Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "crack_expansion",
                "value": round(crack_exp, 2),
                "unit": "mm",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"SOIL_Z{zone_id}",
                "name": f"TDR Soil Moisture Probe Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "soil_moisture",
                "value": round(soil_moist, 1),
                "unit": "%",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"DRATE_Z{zone_id}",
                "name": f"InSAR Displacement Velocity Radar Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "open_pit",
                "sensor_type": "displacement_rate",
                "value": round(disp_rate, 2),
                "unit": "mm/day",
                "status": status,
                "timestamp": now.isoformat(),
            },
        ]

    def generate_underground_reading(self, zone_id: int) -> List[Dict[str, Any]]:
        """
        Generates 6 atmospheric & ventilation sensor readings for an Underground drift/stope zone.
        Injected gas leak targets Zone 4 (Level -150m) or Zone 5 (Sub-Level Stope C).
        Injected fire hazard targets Zone 5 (Sub-Level Stope C).
        """
        now = datetime.now(timezone.utc)
        state = self._zone_states.get(zone_id, {
            "ch4": 0.15, "co": 4.0, "o2": 20.8,
            "temperature": 23.0, "smoke": 0.02, "ventilation": 1.8
        })

        noise = lambda s: random.gauss(0, s)

        is_gas_target = (zone_id in [4, 5])
        is_fire_target = (zone_id in [5, 6])

        is_gas_scenario = (self.current_scenario == "gas_leak" and is_gas_target)
        is_fire_scenario = (self.current_scenario == "fire_hazard" and is_fire_target)
        is_drift = (self.current_scenario == "progressive_drift" and zone_id == 5)

        if is_gas_scenario:
            # Massive methane seam breach + ventilation stall + oxygen displacement
            ch4 = min(4.5, max(1.8, 2.85 + noise(0.25)))
            co = min(120.0, max(45.0, 75.0 + noise(6.0)))
            o2 = max(15.0, min(18.2, 16.8 + noise(0.3)))
            temp = max(22.0, min(32.0, 26.5 + noise(0.8)))
            smoke = max(0.01, min(0.15, 0.04 + noise(0.01)))
            vent = max(0.08, min(0.35, 0.18 + noise(0.04)))
            status = "critical"
        elif is_fire_scenario:
            # Thermal runaway + heavy combustion smoke + severe carbon monoxide
            ch4 = max(0.1, min(1.2, 0.45 + noise(0.08)))
            co = min(220.0, max(85.0, 140.0 + noise(12.0)))
            o2 = max(16.0, min(19.0, 17.5 + noise(0.4)))
            temp = min(75.0, max(48.0, 58.5 + noise(3.5)))
            smoke = min(2.5, max(0.8, 1.45 + noise(0.15)))
            vent = max(0.2, min(0.9, 0.45 + noise(0.08)))
            status = "critical"
        elif is_drift:
            # Progressive gas accumulation
            drift_step = min(15, self.scenario_tick)
            ch4 = max(0.1, state["ch4"] + (drift_step * 0.12) + noise(0.03))
            co = max(2.0, state["co"] + (drift_step * 3.5) + noise(1.0))
            o2 = max(17.5, state["o2"] - (drift_step * 0.18) + noise(0.1))
            temp = max(20.0, state["temperature"] + (drift_step * 0.8) + noise(0.3))
            smoke = max(0.01, state["smoke"] + (drift_step * 0.03) + noise(0.01))
            vent = max(0.3, state["ventilation"] - (drift_step * 0.08) + noise(0.05))
            status = "warning" if drift_step > 5 else "active"
        else:
            # Normal atmospheric conditions
            ch4 = max(0.02, min(0.4, state["ch4"] + noise(0.02)))
            co = max(1.0, min(12.0, state["co"] + noise(0.5)))
            o2 = max(20.2, min(20.95, state["o2"] + noise(0.05)))
            temp = max(21.0, min(26.5, state["temperature"] + noise(0.4)))
            smoke = max(0.005, min(0.06, state["smoke"] + noise(0.005)))
            vent = max(1.2, min(2.5, state["ventilation"] + noise(0.08)))
            status = "active"

        return [
            {
                "sensor_code": f"CH4_Z{zone_id}",
                "name": f"Infrared Methane Optical Detector Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "ch4",
                "value": round(ch4, 3),
                "unit": "%",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"CO_Z{zone_id}",
                "name": f"Electrochemical Carbon Monoxide Sensor Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "co",
                "value": round(co, 1),
                "unit": "ppm",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"O2_Z{zone_id}",
                "name": f"Paramagnetic Oxygen Depletion Cell Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "o2",
                "value": round(o2, 1),
                "unit": "%",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"TEMP_Z{zone_id}",
                "name": f"RTD Sub-Surface Ambient Thermometer Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "temperature",
                "value": round(temp, 1),
                "unit": "°C",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"SMOKE_Z{zone_id}",
                "name": f"Laser Optical Smoke Obscuration Gauge Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "smoke",
                "value": round(smoke, 2),
                "unit": "OD",
                "status": status,
                "timestamp": now.isoformat(),
            },
            {
                "sensor_code": f"VENT_Z{zone_id}",
                "name": f"Ultrasonic Ventilation Anemometer Z{zone_id}",
                "zone_id": zone_id,
                "mine_type": "underground",
                "sensor_type": "ventilation",
                "value": round(vent, 2),
                "unit": "m/s",
                "status": status,
                "timestamp": now.isoformat(),
            },
        ]
