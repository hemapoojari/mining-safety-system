"""
Pydantic Schemas for Emergency Evacuation Alerts and Worker Evacuation Status
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EmergencyAlertBase(BaseModel):
    zone_id: int
    risk_tier: str = Field(..., pattern="^(High|Critical)$")
    hazard_type: str
    message: str


class EmergencyAlertCreate(EmergencyAlertBase):
    alert_code: Optional[str] = None


class EmergencyAlertAck(BaseModel):
    worker_id: int
    status: str = Field(..., pattern="^(acknowledged|evacuating|safe|trapped|Acknowledged|Evacuating|Reached Safe Zone|Alert Sent|notified)$")
    notes: Optional[str] = None


class WorkerEvacuationDetail(BaseModel):
    worker_id: int
    worker_code: str
    full_name: str
    role: str
    phone: Optional[str] = None
    status: str
    acknowledged_at: Optional[datetime] = None
    safe_at: Optional[datetime] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class EmergencyAlertResponse(EmergencyAlertBase):
    id: int
    alert_code: str
    zone_name: Optional[str] = None
    affected_workers_count: int
    acknowledged_count: int
    evacuated_safe_count: int
    trapped_count: int
    is_active: bool
    route_details: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertEvacuationStatusSummary(BaseModel):
    alert_id: int
    alert_code: str
    zone_id: int
    zone_name: str
    risk_tier: str
    hazard_type: str
    is_active: bool
    affected_workers_count: int
    acknowledged_count: int
    evacuated_safe_count: int
    trapped_count: int
    pending_ack_count: int
    route_details: Optional[str] = None
    workers: List[WorkerEvacuationDetail]
