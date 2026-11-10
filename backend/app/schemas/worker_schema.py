"""
Pydantic Schemas for Workers & Real-Time Tracking
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WorkerBase(BaseModel):
    worker_code: str
    full_name: str
    role: str = "Miner"
    phone: Optional[str] = None
    zone_id: Optional[int] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    elevation_or_level: Optional[str] = None
    status: str = "active"


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    zone_id: Optional[int] = None
    status: Optional[str] = None


class WorkerLocationUpdate(BaseModel):
    current_lat: float
    current_lng: float
    elevation_or_level: Optional[str] = None
    zone_id: Optional[int] = None


class WorkerResponse(WorkerBase):
    id: int
    zone_name: Optional[str] = None
    last_ping: datetime

    class Config:
        from_attributes = True


class WorkerEvacuationSummary(BaseModel):
    total_workers: int
    active_workers: int
    off_duty_workers: int
    evacuating_workers: int
    safe_workers: int
    trapped_workers: int
    workers_in_hazardous_zones: int
