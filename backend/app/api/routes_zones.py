"""
Mining Zones Endpoints
Manages zone metadata, polygon geofence coordinates, zone-wise risk queries, and manual risk overrides.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.database.models import MiningZone, Worker, Sensor, SensorReading, RiskPrediction
from backend.app.schemas.zone_schema import (
    MiningZoneResponse,
    MiningZoneCreate,
    MiningZoneRiskUpdate,
    ZoneRiskDetailResponse,
)
from backend.app.services.risk_engine import assess_zone_risk
from backend.app.api.websocket import ws_manager

router = APIRouter(prefix="/api/zones", tags=["Mining Zones"])


@router.get("", response_model=List[MiningZoneResponse], include_in_schema=False)
@router.get("/", response_model=List[MiningZoneResponse])
def get_all_zones(
    mine_type: Optional[str] = Query(None, description="Filter by open_pit or underground"),
    db: Session = Depends(get_db),
):
    """Retrieve all mining zones with active worker and sensor counts."""
    query = db.query(MiningZone)
    if mine_type:
        query = query.filter(MiningZone.mine_type == mine_type)
    zones = query.all()

    results = []
    for z in zones:
        w_count = db.query(Worker).filter(Worker.zone_id == z.id).count()
        s_count = db.query(Sensor).filter(Sensor.zone_id == z.id).count()
        results.append(
            MiningZoneResponse(
                id=z.id,
                zone_code=z.zone_code,
                name=z.name,
                mine_type=z.mine_type,
                description=z.description,
                boundary_geo=z.boundary_geo,
                current_risk_tier=z.current_risk_tier,
                updated_at=z.updated_at,
                active_worker_count=w_count,
                sensor_count=s_count,
            )
        )
    return results


@router.post("/", response_model=MiningZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(zone_in: MiningZoneCreate, db: Session = Depends(get_db)):
    """Define a new mine zone with geofence polygon coordinates."""
    existing = db.query(MiningZone).filter(MiningZone.zone_code == zone_in.zone_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Zone code {zone_in.zone_code} already exists.")

    zone = MiningZone(
        zone_code=zone_in.zone_code,
        name=zone_in.name,
        mine_type=zone_in.mine_type,
        description=zone_in.description,
        boundary_geo=zone_in.boundary_geo,
        current_risk_tier=zone_in.current_risk_tier,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)

    return MiningZoneResponse(
        id=zone.id,
        zone_code=zone.zone_code,
        name=zone.name,
        mine_type=zone.mine_type,
        description=zone.description,
        boundary_geo=zone.boundary_geo,
        current_risk_tier=zone.current_risk_tier,
        updated_at=zone.updated_at,
        active_worker_count=0,
        sensor_count=0,
    )


@router.get("/{zone_id_or_code}", response_model=MiningZoneResponse)
def get_zone_detail(zone_id_or_code: str, db: Session = Depends(get_db)):
    """Retrieve detailed metadata for an individual mining zone."""
    zone = None
    if zone_id_or_code.isdigit():
        zone = db.query(MiningZone).filter(MiningZone.id == int(zone_id_or_code)).first()
    if not zone:
        zone = db.query(MiningZone).filter(MiningZone.zone_code == zone_id_or_code).first()

    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id_or_code} not found.")

    w_count = db.query(Worker).filter(Worker.zone_id == zone.id).count()
    s_count = db.query(Sensor).filter(Sensor.zone_id == zone.id).count()

    return MiningZoneResponse(
        id=zone.id,
        zone_code=zone.zone_code,
        name=zone.name,
        mine_type=zone.mine_type,
        description=zone.description,
        boundary_geo=zone.boundary_geo,
        current_risk_tier=zone.current_risk_tier,
        updated_at=zone.updated_at,
        active_worker_count=w_count,
        sensor_count=s_count,
    )


@router.get("/{zone_id_or_code}/risk", response_model=ZoneRiskDetailResponse)
def get_zone_risk_detail(zone_id_or_code: str, db: Session = Depends(get_db)):
    """
    Computes and returns the detailed risk evaluation breakdown for the given zone
    using current sensor readings and threshold rules.
    """
    zone = None
    if zone_id_or_code.isdigit():
        zone = db.query(MiningZone).filter(MiningZone.id == int(zone_id_or_code)).first()
    if not zone:
        zone = db.query(MiningZone).filter(MiningZone.zone_code == zone_id_or_code).first()

    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id_or_code} not found.")

    # Fetch latest reading per sensor type
    latest_readings = (
        db.query(SensorReading.sensor_type, SensorReading.value)
        .filter(SensorReading.zone_id == zone.id)
        .order_by(desc(SensorReading.timestamp))
        .limit(20)
        .all()
    )
    snapshot = {}
    for stype, sval in latest_readings:
        if stype not in snapshot:
            snapshot[stype] = sval

    # Run assessment
    risk_eval = assess_zone_risk(zone.mine_type, snapshot)
    w_count = db.query(Worker).filter(Worker.zone_id == zone.id).count()

    return ZoneRiskDetailResponse(
        zone_id=zone.id,
        zone_code=zone.zone_code,
        name=zone.name,
        mine_type=zone.mine_type,
        current_risk_tier=zone.current_risk_tier,
        composite_risk_score=risk_eval["composite_score"],
        hazard_breakdown=risk_eval["breakdown"],
        active_hazard=risk_eval["dominant_hazard"],
        affected_worker_count=w_count,
        last_evaluated=datetime.now(timezone.utc),
    )


@router.patch("/{zone_id_or_code}/risk", response_model=MiningZoneResponse)
async def update_zone_risk(
    zone_id_or_code: str,
    update_in: MiningZoneRiskUpdate,
    db: Session = Depends(get_db),
):
    """Manual safety officer override for a zone's risk status."""
    zone = None
    if zone_id_or_code.isdigit():
        zone = db.query(MiningZone).filter(MiningZone.id == int(zone_id_or_code)).first()
    if not zone:
        zone = db.query(MiningZone).filter(MiningZone.zone_code == zone_id_or_code).first()

    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id_or_code} not found.")

    prev_tier = zone.current_risk_tier
    zone.current_risk_tier = update_in.risk_tier
    zone.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(zone)

    # Broadcast manual risk update
    await ws_manager.broadcast(
        event_type="RISK_UPDATE",
        data={
            "zone_id": zone.id,
            "zone_name": zone.name,
            "mine_type": zone.mine_type,
            "previous_risk_tier": prev_tier,
            "current_risk_tier": zone.current_risk_tier,
            "reason": update_in.reason or "Manual safety officer override",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    w_count = db.query(Worker).filter(Worker.zone_id == zone.id).count()
    s_count = db.query(Sensor).filter(Sensor.zone_id == zone.id).count()

    return MiningZoneResponse(
        id=zone.id,
        zone_code=zone.zone_code,
        name=zone.name,
        mine_type=zone.mine_type,
        description=zone.description,
        boundary_geo=zone.boundary_geo,
        current_risk_tier=zone.current_risk_tier,
        updated_at=zone.updated_at,
        active_worker_count=w_count,
        sensor_count=s_count,
    )
