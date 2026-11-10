"""
Pydantic Schemas for Mining Zones
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class MiningZoneBase(BaseModel):
    zone_code: str
    name: str
    mine_type: str = Field(..., pattern="^(open_pit|underground)$")
    description: Optional[str] = None
    boundary_geo: Optional[str] = None  # JSON string of [[lat, lng], ...]
    current_risk_tier: str = "Safe"


class MiningZoneCreate(MiningZoneBase):
    pass


class MiningZoneRiskUpdate(BaseModel):
    risk_tier: str = Field(..., pattern="^(Safe|Low|Medium|High|Critical)$")
    reason: Optional[str] = None


class MiningZoneResponse(MiningZoneBase):
    id: int
    updated_at: datetime
    active_worker_count: int = 0
    sensor_count: int = 0

    class Config:
        from_attributes = True


class ZoneRiskDetailResponse(BaseModel):
    zone_id: int
    zone_code: str
    name: str
    mine_type: str
    current_risk_tier: str
    composite_risk_score: float
    hazard_breakdown: Dict[str, Any]
    active_hazard: Optional[str] = None
    affected_worker_count: int = 0
    last_evaluated: datetime
