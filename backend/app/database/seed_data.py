"""
Database Seeding Script
Populates realistic initial records for Open-Pit and Underground mining zones,
registered workers, geotechnical & atmospheric sensors, and baseline telemetry.
"""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.database.session import SessionLocal, engine, Base
from backend.app.database.models import (
    MiningZone,
    Worker,
    Sensor,
    SensorReading,
    RiskPrediction,
)

logger = logging.getLogger("mining_safety.seed")


def seed_database(db: Session = None):
    """Seeds the database if tables are empty."""
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True

    try:
        # Check if already seeded
        if db.query(MiningZone).count() > 0:
            logger.info("Database already seeded with mining zones. Skipping.")
            return

        logger.info("Starting database seeding...")

        # -------------------------------------------------------------
        # 1. MINING ZONES
        # -------------------------------------------------------------
        # Reference coordinates: 23.7450° N, 86.4150° E (Dhanbad Coal/Mineral Mining Basin)
        zones_data = [
            # Open-Pit Zones
            {
                "zone_code": "OP-Z1",
                "name": "North Bench #1 (Upper Wall)",
                "mine_type": "open_pit",
                "description": "High-altitude extraction bench subject to slope stability monitoring and precipitation runoff.",
                "boundary_geo": json.dumps([
                    [23.7460, 86.4140],
                    [23.7475, 86.4155],
                    [23.7465, 86.4170],
                    [23.7450, 86.4155],
                ]),
                "current_risk_tier": "Safe",
            },
            {
                "zone_code": "OP-Z2",
                "name": "East Highwall & Slope Cut",
                "mine_type": "open_pit",
                "description": "Steep rock cut face equipped with extensometers for rockfall and kinematic failure warning.",
                "boundary_geo": json.dumps([
                    [23.7450, 86.4170],
                    [23.7465, 86.4185],
                    [23.7450, 86.4200],
                    [23.7435, 86.4185],
                ]),
                "current_risk_tier": "Safe",
            },
            {
                "zone_code": "OP-Z3",
                "name": "Main Haulage Ramp & Crushing Hub",
                "mine_type": "open_pit",
                "description": "Heavy machinery transit route for 100T dumpers and mobile rock breakers.",
                "boundary_geo": json.dumps([
                    [23.7435, 86.4135],
                    [23.7450, 86.4150],
                    [23.7440, 86.4165],
                    [23.7425, 86.4150],
                ]),
                "current_risk_tier": "Safe",
            },
            # Underground Zones
            {
                "zone_code": "UG-Z1",
                "name": "Shaft #2 Level -150m Extraction Drift",
                "mine_type": "underground",
                "description": "Sub-surface active development roadway with continuous toxic gas and airflow surveillance.",
                "boundary_geo": json.dumps([
                    [23.7420, 86.4120],
                    [23.7430, 86.4130],
                    [23.7425, 86.4140],
                    [23.7415, 86.4130],
                ]),
                "current_risk_tier": "Safe",
            },
            {
                "zone_code": "UG-Z2",
                "name": "Sub-Level Stope C (Production Face)",
                "mine_type": "underground",
                "description": "Deep stoping chamber with high spontaneous combustion potential and methane hazard.",
                "boundary_geo": json.dumps([
                    [23.7410, 86.4130],
                    [23.7420, 86.4140],
                    [23.7415, 86.4150],
                    [23.7405, 86.4140],
                ]),
                "current_risk_tier": "Safe",
            },
            {
                "zone_code": "UG-Z3",
                "name": "South Return Airway & Exhaust Fan Station",
                "mine_type": "underground",
                "description": "Primary return ventilation airway directing exhaust air to surface vent shafts.",
                "boundary_geo": json.dumps([
                    [23.7400, 86.4140],
                    [23.7410, 86.4150],
                    [23.7405, 86.4160],
                    [23.7395, 86.4150],
                ]),
                "current_risk_tier": "Safe",
            },
        ]

        created_zones = {}
        for z in zones_data:
            zone_obj = MiningZone(**z, updated_at=datetime.now(timezone.utc))
            db.add(zone_obj)
            db.flush()
            created_zones[z["zone_code"]] = zone_obj

        # -------------------------------------------------------------
        # 2. WORKERS
        # -------------------------------------------------------------
        workers_data = [
            {
                "worker_code": "WRK-1001",
                "full_name": "Rajesh Kumar",
                "role": "Excavator Operator",
                "phone": "+91-9876543201",
                "zone_id": created_zones["OP-Z1"].id,
                "current_lat": 23.7462,
                "current_lng": 86.4152,
                "elevation_or_level": "Bench #1 Upper (+310m)",
                "status": "active",
            },
            {
                "worker_code": "WRK-1002",
                "full_name": "Amit Sharma",
                "role": "Geotechnical Drill Tech",
                "phone": "+91-9876543202",
                "zone_id": created_zones["OP-Z2"].id,
                "current_lat": 23.7452,
                "current_lng": 86.4182,
                "elevation_or_level": "East Cut (+280m)",
                "status": "active",
            },
            {
                "worker_code": "WRK-1003",
                "full_name": "Manoj Singh",
                "role": "Haul Truck Driver",
                "phone": "+91-9876543203",
                "zone_id": created_zones["OP-Z3"].id,
                "current_lat": 23.7438,
                "current_lng": 86.4148,
                "elevation_or_level": "Main Ramp (+240m)",
                "status": "active",
            },
            {
                "worker_code": "WRK-1004",
                "full_name": "Suresh Patel",
                "role": "Underground LHD Operator",
                "phone": "+91-9876543204",
                "zone_id": created_zones["UG-Z1"].id,
                "current_lat": 23.7423,
                "current_lng": 86.4128,
                "elevation_or_level": "Level -150m",
                "status": "active",
            },
            {
                "worker_code": "WRK-1005",
                "full_name": "Vikram Das",
                "role": "Blasting & Strata Support",
                "phone": "+91-9876543205",
                "zone_id": created_zones["UG-Z2"].id,
                "current_lat": 23.7413,
                "current_lng": 86.4138,
                "elevation_or_level": "Sub-Level Stope C (-200m)",
                "status": "active",
            },
            {
                "worker_code": "WRK-1006",
                "full_name": "Aniket Roy",
                "role": "Ventilation Officer",
                "phone": "+91-9876543206",
                "zone_id": created_zones["UG-Z3"].id,
                "current_lat": 23.7403,
                "current_lng": 86.4148,
                "elevation_or_level": "Return Airway Station",
                "status": "active",
            },
            {
                "worker_code": "WRK-1007",
                "full_name": "Deepa Nair",
                "role": "Chief Mine Safety Officer",
                "phone": "+91-9876543207",
                "zone_id": created_zones["OP-Z3"].id,
                "current_lat": 23.7445,
                "current_lng": 86.4150,
                "elevation_or_level": "Surface Command Station",
                "status": "active",
            },
        ]

        for w in workers_data:
            w_obj = Worker(**w, last_ping=datetime.now(timezone.utc))
            db.add(w_obj)

        # -------------------------------------------------------------
        # 3. SENSORS (GEOTECHNICAL & ATMOSPHERIC)
        # -------------------------------------------------------------
        sensors_data = [
            # Open-Pit Sensors
            {
                "sensor_code": "RAIN-01",
                "name": "North Rim Tipping Bucket Rain Gauge",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "rainfall",
                "unit": "mm/h",
                "status": "active",
            },
            {
                "sensor_code": "VIB-01",
                "name": "North Bench Tri-Axial Geophone (PPV)",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "vibration",
                "unit": "mm/s",
                "status": "active",
            },
            {
                "sensor_code": "SLOPE-01",
                "name": "North Bench Multi-Point Extensometer",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "slope_displacement",
                "unit": "mm",
                "status": "active",
            },
            {
                "sensor_code": "VIB-02",
                "name": "East Highwall Seismic Sensor",
                "zone_id": created_zones["OP-Z2"].id,
                "mine_type": "open_pit",
                "sensor_type": "vibration",
                "unit": "mm/s",
                "status": "active",
            },
            {
                "sensor_code": "SLOPE-02",
                "name": "East Highwall Vibrating Wire Crackmeter",
                "zone_id": created_zones["OP-Z2"].id,
                "mine_type": "open_pit",
                "sensor_type": "slope_displacement",
                "unit": "mm",
                "status": "active",
            },
            {
                "sensor_code": "RAIN-02",
                "name": "Main Ramp Weather & Precipitation Station",
                "zone_id": created_zones["OP-Z3"].id,
                "mine_type": "open_pit",
                "sensor_type": "rainfall",
                "unit": "mm/h",
                "status": "active",
            },
            {
                "sensor_code": "CRACK-01",
                "name": "North Bench Vibrating Wire Crackmeter",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "crack_expansion",
                "unit": "mm",
                "status": "active",
            },
            {
                "sensor_code": "SOIL-01",
                "name": "North Bench TDR Soil Moisture Probe",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "soil_moisture",
                "unit": "%",
                "status": "active",
            },
            {
                "sensor_code": "DRATE-01",
                "name": "North Bench Displacement Velocity Radar",
                "zone_id": created_zones["OP-Z1"].id,
                "mine_type": "open_pit",
                "sensor_type": "displacement_rate",
                "unit": "mm/day",
                "status": "active",
            },
            # Underground Sensors
            {
                "sensor_code": "CH4-01",
                "name": "Shaft 2 Catalytic Methane Monitor",
                "zone_id": created_zones["UG-Z1"].id,
                "mine_type": "underground",
                "sensor_type": "ch4",
                "unit": "%",
                "status": "active",
            },
            {
                "sensor_code": "CO-01",
                "name": "Shaft 2 Electrochemical Carbon Monoxide Sensor",
                "zone_id": created_zones["UG-Z1"].id,
                "mine_type": "underground",
                "sensor_type": "co",
                "unit": "ppm",
                "status": "active",
            },
            {
                "sensor_code": "O2-01",
                "name": "Shaft 2 Paramagnetic Oxygen Detector",
                "zone_id": created_zones["UG-Z1"].id,
                "mine_type": "underground",
                "sensor_type": "o2",
                "unit": "%",
                "status": "active",
            },
            {
                "sensor_code": "TEMP-01",
                "name": "Stope C Thermal Infrared Pyrometer",
                "zone_id": created_zones["UG-Z2"].id,
                "mine_type": "underground",
                "sensor_type": "temperature",
                "unit": "°C",
                "status": "active",
            },
            {
                "sensor_code": "SMOKE-01",
                "name": "Stope C Optical Smoke Density Sensor",
                "zone_id": created_zones["UG-Z2"].id,
                "mine_type": "underground",
                "sensor_type": "smoke",
                "unit": "OD",
                "status": "active",
            },
            {
                "sensor_code": "CH4-02",
                "name": "Stope C Continuous Methane Sensor",
                "zone_id": created_zones["UG-Z2"].id,
                "mine_type": "underground",
                "sensor_type": "ch4",
                "unit": "%",
                "status": "active",
            },
            {
                "sensor_code": "VENT-01",
                "name": "South Return Ultrasonic Anemometer",
                "zone_id": created_zones["UG-Z3"].id,
                "mine_type": "underground",
                "sensor_type": "ventilation",
                "unit": "m/s",
                "status": "active",
            },
            {
                "sensor_code": "CO-02",
                "name": "South Return Exhaust Air CO Detector",
                "zone_id": created_zones["UG-Z3"].id,
                "mine_type": "underground",
                "sensor_type": "co",
                "unit": "ppm",
                "status": "active",
            },
        ]

        created_sensors = {}
        for s in sensors_data:
            s_obj = Sensor(**s, installed_at=datetime.now(timezone.utc))
            db.add(s_obj)
            db.flush()
            created_sensors[s["sensor_code"]] = s_obj

        # -------------------------------------------------------------
        # 4. INITIAL SENSOR READINGS (NOMINAL / BASELINE)
        # -------------------------------------------------------------
        initial_readings = [
            ("RAIN-01", 1.2),
            ("VIB-01", 0.45),
            ("SLOPE-01", 0.15),
            ("VIB-02", 0.60),
            ("SLOPE-02", 0.22),
            ("RAIN-02", 0.8),
            ("CH4-01", 0.12),
            ("CO-01", 4.5),
            ("O2-01", 20.8),
            ("TEMP-01", 24.5),
            ("SMOKE-01", 0.02),
            ("CH4-02", 0.18),
            ("VENT-01", 1.85),
            ("CO-02", 5.2),
        ]

        now = datetime.now(timezone.utc)
        for scode, val in initial_readings:
            s_obj = created_sensors[scode]
            reading = SensorReading(
                sensor_id=s_obj.id,
                sensor_code=s_obj.sensor_code,
                zone_id=s_obj.zone_id,
                mine_type=s_obj.mine_type,
                sensor_type=s_obj.sensor_type,
                value=val,
                unit=s_obj.unit,
                timestamp=now,
            )
            db.add(reading)

        db.commit()
        logger.info("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        if close_at_end:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(bind=engine)
    seed_database()
