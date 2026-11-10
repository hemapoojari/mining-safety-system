"""
Pydantic Schemas for Sensors and Sensor Telemetry Readings
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ------------------ Sensor Definition Schemas ------------------

class SensorBase(BaseModel):
    sensor_code: str
    name: str
    zone_id: int
    mine_type: str = Field(..., pattern="^(open_pit|underground)$")
    sensor_type: str  # rainfall, vibration, slope_displacement, ch4, co, o2, temperature, smoke, ventilation
    unit: str
    status: str = "active"


class SensorCreate(SensorBase):
    pass


class SensorResponse(SensorBase):
    id: int
    installed_at: datetime

    class Config:
        from_attributes = True


# ------------------ Sensor Reading Schemas ------------------

class SensorReadingBase(BaseModel):
    sensor_code: str
    zone_id: int
    mine_type: str = Field(..., pattern="^(open_pit|underground)$")
    sensor_type: str
    value: float
    unit: str
    sensor_id: Optional[int] = None


class SensorReadingCreate(SensorReadingBase):
    timestamp: Optional[datetime] = None


class SensorReadingResponse(SensorReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class CurrentSensorReadingResponse(BaseModel):
    sensor_code: str
    name: str
    zone_id: int
    zone_name: str
    mine_type: str
    sensor_type: str
    latest_value: float
    unit: str
    status: str
    last_updated: datetime


class ZoneTelemetrySummary(BaseModel):
    zone_id: int
    zone_name: str
    zone_code: str
    mine_type: str
    current_risk_tier: str
    readings: Dict[str, Any]
    last_updated: datetime
