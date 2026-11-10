"""
Worker Monitoring & Geolocation Endpoints
Manages worker registration, real-time spatial positioning, geofencing correlation,
and evacuation status tracking.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.database.models import Worker, MiningZone
from backend.app.schemas.worker_schema import (
    WorkerResponse,
    WorkerCreate,
    WorkerUpdate,
    WorkerLocationUpdate,
    WorkerEvacuationSummary,
)
from backend.app.services.geofence_service import resolve_zone_for_coordinates
from backend.app.api.websocket import ws_manager

router = APIRouter(prefix="/api/workers", tags=["Workers"])


@router.get("", response_model=List[WorkerResponse], include_in_schema=False)
@router.get("/", response_model=List[WorkerResponse])
def get_all_workers(
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    status: Optional[str] = Query(None, description="Filter by status (active, evacuating, safe, trapped, off_duty)"),
    db: Session = Depends(get_db),
):
    """Retrieve all registered mine workers with their current coordinates and assigned zones."""
    query = db.query(Worker)
    if zone_id is not None:
        query = query.filter(Worker.zone_id == zone_id)
    if status is not None:
        query = query.filter(Worker.status == status)

    workers = query.all()
    results = []
    for w in workers:
        zone_name = w.zone.name if w.zone else "Unassigned / Transit"
        results.append(
            WorkerResponse(
                id=w.id,
                worker_code=w.worker_code,
                full_name=w.full_name,
                role=w.role,
                phone=w.phone,
                zone_id=w.zone_id,
                zone_name=zone_name,
                current_lat=w.current_lat,
                current_lng=w.current_lng,
                elevation_or_level=w.elevation_or_level,
                status=w.status,
                last_ping=w.last_ping,
            )
        )
    return results


@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def register_worker(
    worker_in: WorkerCreate,
    db: Session = Depends(get_db),
):
    """Register a new personnel record into the mining safety system."""
    existing = db.query(Worker).filter(Worker.worker_code == worker_in.worker_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Worker with code {worker_in.worker_code} already exists.")

    if worker_in.zone_id:
        zone = db.query(MiningZone).filter(MiningZone.id == worker_in.zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail=f"Zone ID {worker_in.zone_id} not found.")

    worker = Worker(
        worker_code=worker_in.worker_code,
        full_name=worker_in.full_name,
        role=worker_in.role,
        phone=worker_in.phone,
        zone_id=worker_in.zone_id,
        current_lat=worker_in.current_lat,
        current_lng=worker_in.current_lng,
        elevation_or_level=worker_in.elevation_or_level,
        status=worker_in.status,
        last_ping=datetime.now(timezone.utc),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    return WorkerResponse(
        id=worker.id,
        worker_code=worker.worker_code,
        full_name=worker.full_name,
        role=worker.role,
        phone=worker.phone,
        zone_id=worker.zone_id,
        zone_name=worker.zone.name if worker.zone else None,
        current_lat=worker.current_lat,
        current_lng=worker.current_lng,
        elevation_or_level=worker.elevation_or_level,
        status=worker.status,
        last_ping=worker.last_ping,
    )


@router.get("/evacuation/summary", response_model=WorkerEvacuationSummary)
def get_evacuation_summary(db: Session = Depends(get_db)):
    """Summary of worker availability, statuses, and counts in hazardous zones."""
    total = db.query(Worker).count()
    active = db.query(Worker).filter(Worker.status == "active").count()
    off_duty = db.query(Worker).filter(Worker.status == "off_duty").count()
    evacuating = db.query(Worker).filter(Worker.status == "evacuating").count()
    safe = db.query(Worker).filter(Worker.status == "safe").count()
    trapped = db.query(Worker).filter(Worker.status == "trapped").count()

    # Query workers in zones where current_risk_tier is High or Critical
    hazardous_zones = db.query(MiningZone.id).filter(MiningZone.current_risk_tier.in_(["High", "Critical"])).all()
    h_zone_ids = [z[0] for z in hazardous_zones]
    in_danger = db.query(Worker).filter(Worker.zone_id.in_(h_zone_ids)).count() if h_zone_ids else 0

    return WorkerEvacuationSummary(
        total_workers=total,
        active_workers=active,
        off_duty_workers=off_duty,
        evacuating_workers=evacuating,
        safe_workers=safe,
        trapped_workers=trapped,
        workers_in_hazardous_zones=in_danger,
    )


@router.get("/zone/{zone_id}", response_model=List[WorkerResponse])
def get_workers_by_zone(zone_id: int, db: Session = Depends(get_db)):
    """Retrieve all workers currently present in a specified zone."""
    zone = db.query(MiningZone).filter(MiningZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone ID {zone_id} not found.")

    workers = db.query(Worker).filter(Worker.zone_id == zone_id).all()
    return [
        WorkerResponse(
            id=w.id,
            worker_code=w.worker_code,
            full_name=w.full_name,
            role=w.role,
            phone=w.phone,
            zone_id=w.zone_id,
            zone_name=zone.name,
            current_lat=w.current_lat,
            current_lng=w.current_lng,
            elevation_or_level=w.elevation_or_level,
            status=w.status,
            last_ping=w.last_ping,
        )
        for w in workers
    ]


@router.get("/{worker_id_or_code}", response_model=WorkerResponse)
def get_worker_detail(worker_id_or_code: str, db: Session = Depends(get_db)):
    """Retrieve detailed record for a specific worker by ID or worker code."""
    worker = None
    if worker_id_or_code.isdigit():
        worker = db.query(Worker).filter(Worker.id == int(worker_id_or_code)).first()
    if not worker:
        worker = db.query(Worker).filter(Worker.worker_code == worker_id_or_code).first()

    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker {worker_id_or_code} not found.")

    return WorkerResponse(
        id=worker.id,
        worker_code=worker.worker_code,
        full_name=worker.full_name,
        role=worker.role,
        phone=worker.phone,
        zone_id=worker.zone_id,
        zone_name=worker.zone.name if worker.zone else None,
        current_lat=worker.current_lat,
        current_lng=worker.current_lng,
        elevation_or_level=worker.elevation_or_level,
        status=worker.status,
        last_ping=worker.last_ping,
    )


@router.post("/{worker_id_or_code}/location", response_model=WorkerResponse)
async def update_worker_location(
    worker_id_or_code: str,
    loc_in: WorkerLocationUpdate,
    db: Session = Depends(get_db),
):
    """
    Update live worker GPS or indoor grid coordinates.
    Runs spatial geofencing to auto-detect and update current zone, and broadcasts update.
    """
    worker = None
    if worker_id_or_code.isdigit():
        worker = db.query(Worker).filter(Worker.id == int(worker_id_or_code)).first()
    if not worker:
        worker = db.query(Worker).filter(Worker.worker_code == worker_id_or_code).first()

    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker {worker_id_or_code} not found.")

    worker.current_lat = loc_in.current_lat
    worker.current_lng = loc_in.current_lng
    if loc_in.elevation_or_level:
        worker.elevation_or_level = loc_in.elevation_or_level

    # Spatial geofence check
    all_zones = db.query(MiningZone).all()
    matched_zone = resolve_zone_for_coordinates(loc_in.current_lat, loc_in.current_lng, all_zones)
    if matched_zone:
        worker.zone_id = matched_zone.id
    elif loc_in.zone_id:
        worker.zone_id = loc_in.zone_id

    worker.last_ping = datetime.now(timezone.utc)
    db.commit()
    db.refresh(worker)

    zone_name = worker.zone.name if worker.zone else "Unassigned / Transit"

    # Broadcast WORKER_LOCATION via WebSockets
    await ws_manager.broadcast(
        event_type="WORKER_LOCATION",
        data={
            "worker_id": worker.id,
            "worker_code": worker.worker_code,
            "full_name": worker.full_name,
            "current_lat": worker.current_lat,
            "current_lng": worker.current_lng,
            "elevation_or_level": worker.elevation_or_level,
            "zone_id": worker.zone_id,
            "zone_name": zone_name,
            "status": worker.status,
            "last_ping": worker.last_ping.isoformat(),
        },
    )

    return WorkerResponse(
        id=worker.id,
        worker_code=worker.worker_code,
        full_name=worker.full_name,
        role=worker.role,
        phone=worker.phone,
        zone_id=worker.zone_id,
        zone_name=zone_name,
        current_lat=worker.current_lat,
        current_lng=worker.current_lng,
        elevation_or_level=worker.elevation_or_level,
        status=worker.status,
        last_ping=worker.last_ping,
    )
