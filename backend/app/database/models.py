"""
SQLAlchemy ORM Models
Defines relational schemas for Mining Zones, Workers, Sensors, Sensor Readings,
Risk Predictions, Emergency Alerts, and Worker Evacuation Statuses.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class MiningZone(Base):
    __tablename__ = "mining_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    mine_type = Column(String(20), nullable=False)  # "open_pit" or "underground"
    description = Column(String(255), nullable=True)
    boundary_geo = Column(Text, nullable=True)  # JSON string of coordinates [[lat, lng], ...]
    current_risk_tier = Column(String(20), default="Safe", nullable=False)  # Safe, Low, Medium, High, Critical
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workers = relationship("Worker", back_populates="zone", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="zone", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="zone", cascade="all, delete-orphan")
    predictions = relationship("RiskPrediction", back_populates="zone", cascade="all, delete-orphan")
    alerts = relationship("EmergencyAlert", back_populates="zone", cascade="all, delete-orphan")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    worker_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Miner", nullable=False)  # Operator, Driller, Geologist, Safety Officer, Blaster
    phone = Column(String(30), nullable=True)
    zone_id = Column(Integer, ForeignKey("mining_zones.id", ondelete="SET NULL"), nullable=True)
    
    # Location Tracking
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    elevation_or_level = Column(String(50), nullable=True)  # e.g., "Level -150m" or "Bench #2"
    
    # Worker Status: "active", "off_duty", "evacuating", "safe", "trapped"
    status = Column(String(30), default="active", nullable=False)
    last_ping = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    zone = relationship("MiningZone", back_populates="workers")
    evacuation_statuses = relationship("WorkerEvacuationStatus", back_populates="worker", cascade="all, delete-orphan")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    zone_id = Column(Integer, ForeignKey("mining_zones.id", ondelete="CASCADE"), nullable=False)
    mine_type = Column(String(20), nullable=False)  # "open_pit" or "underground"
    sensor_type = Column(String(50), nullable=False)  # rainfall, vibration, slope_displacement, ch4, co, o2, temperature, smoke, ventilation
    unit = Column(String(20), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # "active", "maintenance", "offline"
    installed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    zone = relationship("MiningZone", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id", ondelete="CASCADE"), nullable=True)
    sensor_code = Column(String(50), index=True, nullable=False)
    zone_id = Column(Integer, ForeignKey("mining_zones.id", ondelete="CASCADE"), nullable=False)
    mine_type = Column(String(20), nullable=False)  # "open_pit" or "underground"
    sensor_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    zone = relationship("MiningZone", back_populates="sensor_readings")
    sensor = relationship("Sensor", back_populates="readings")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("mining_zones.id", ondelete="CASCADE"), nullable=False)
    mine_type = Column(String(20), nullable=False)  # "open_pit" or "underground"
    hazard_type = Column(String(50), nullable=False)  # slope_failure, rockfall, toxic_gas, fire_hazard
    risk_score = Column(Float, nullable=False)  # Normalized 0.0 to 1.0
    risk_tier = Column(String(20), nullable=False)  # Safe, Low, Medium, High, Critical
    confidence = Column(Float, default=0.95, nullable=True)
    model_name = Column(String(50), default="ML_Ensemble", nullable=True)
    calculation_method = Column(String(50), default="threshold_rule_engine", nullable=False)
    details = Column(Text, nullable=True)  # JSON string with metrics breakdown
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    zone = relationship("MiningZone", back_populates="predictions")


class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_code = Column(String(50), unique=True, index=True, nullable=False)
    zone_id = Column(Integer, ForeignKey("mining_zones.id", ondelete="CASCADE"), nullable=False)
    risk_tier = Column(String(20), nullable=False)  # High or Critical
    hazard_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    
    # Aggregated evacuation metrics
    affected_workers_count = Column(Integer, default=0)
    acknowledged_count = Column(Integer, default=0)
    evacuated_safe_count = Column(Integer, default=0)
    trapped_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True, index=True)
    route_details = Column(Text, nullable=True)  # JSON string of route waypoints, destination, and status
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    zone = relationship("MiningZone", back_populates="alerts")
    evacuation_statuses = relationship("WorkerEvacuationStatus", back_populates="alert", cascade="all, delete-orphan")


class WorkerEvacuationStatus(Base):
    __tablename__ = "worker_evacuation_status"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("emergency_alerts.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    
    # Status: "notified", "acknowledged", "evacuating", "safe", "trapped"
    status = Column(String(30), default="notified", nullable=False)
    notes = Column(String(255), nullable=True)
    
    acknowledged_at = Column(DateTime, nullable=True)
    safe_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    alert = relationship("EmergencyAlert", back_populates="evacuation_statuses")
    worker = relationship("Worker", back_populates="evacuation_statuses")
