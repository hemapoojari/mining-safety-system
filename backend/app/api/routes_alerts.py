"""
Emergency Alerts & Targeted Evacuation Endpoints
Triggers zone-specific emergency alarms, targeted notification dispatches,
worker 2-way acknowledgements, and evacuation audit monitors.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.database.models import EmergencyAlert, WorkerEvacuationStatus, MiningZone, Worker
from backend.app.schemas.alert_schema import (
    EmergencyAlertResponse,
    EmergencyAlertCreate,
    EmergencyAlertAck,
    AlertEvacuationStatusSummary,
    WorkerEvacuationDetail,
)
from backend.app.services.alert_service import (
    trigger_emergency_evacuation,
    process_worker_acknowledgement,
    resolve_emergency_alert,
)
from backend.app.api.websocket import ws_manager

router = APIRouter(prefix="/api/alerts", tags=["Emergency Alerts"])


@router.get("/active", response_model=List[EmergencyAlertResponse])
def get_active_emergency_alerts(db: Session = Depends(get_db)):
    """Retrieve all ongoing, unresolved emergency alerts."""
    alerts = (
        db.query(EmergencyAlert)
        .filter(EmergencyAlert.is_active == True)
        .order_by(desc(EmergencyAlert.created_at))
        .all()
    )
    results = []
    for a in alerts:
        results.append(
            EmergencyAlertResponse(
                id=a.id,
                alert_code=a.alert_code,
                zone_id=a.zone_id,
                zone_name=a.zone.name if a.zone else f"Zone {a.zone_id}",
                risk_tier=a.risk_tier,
                hazard_type=a.hazard_type,
                message=a.message,
                affected_workers_count=a.affected_workers_count,
                acknowledged_count=a.acknowledged_count,
                evacuated_safe_count=a.evacuated_safe_count,
                trapped_count=a.trapped_count,
                is_active=a.is_active,
                route_details=a.route_details,
                created_at=a.created_at,
                resolved_at=a.resolved_at,
            )
        )
    return results


@router.get("/history", response_model=List[EmergencyAlertResponse])
def get_alert_history(
    zone_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve historical emergency alert records."""
    query = db.query(EmergencyAlert)
    if zone_id:
        query = query.filter(EmergencyAlert.zone_id == zone_id)
    alerts = query.order_by(desc(EmergencyAlert.created_at)).limit(limit).all()

    return [
        EmergencyAlertResponse(
            id=a.id,
            alert_code=a.alert_code,
            zone_id=a.zone_id,
            zone_name=a.zone.name if a.zone else f"Zone {a.zone_id}",
            risk_tier=a.risk_tier,
            hazard_type=a.hazard_type,
            message=a.message,
            affected_workers_count=a.affected_workers_count,
            acknowledged_count=a.acknowledged_count,
            evacuated_safe_count=a.evacuated_safe_count,
            trapped_count=a.trapped_count,
            is_active=a.is_active,
            route_details=a.route_details,
            created_at=a.created_at,
            resolved_at=a.resolved_at,
        )
        for a in alerts
    ]


@router.post("/trigger", response_model=EmergencyAlertResponse, status_code=status.HTTP_201_CREATED)
async def trigger_alert(
    alert_in: EmergencyAlertCreate,
    db: Session = Depends(get_db),
):
    """
    Triggers an emergency evacuation alert for a specific mining zone.
    Locates all workers in that zone and initializes targeted evacuation records.
    Broadcasts high-priority alert via WebSockets.
    """
    try:
        alert = trigger_emergency_evacuation(
            db=db,
            zone_id=alert_in.zone_id,
            risk_tier=alert_in.risk_tier,
            hazard_type=alert_in.hazard_type,
            message=alert_in.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Broadcast EMERGENCY_ALERT
    await ws_manager.broadcast(
        event_type="EMERGENCY_ALERT",
        data={
            "alert_id": alert.id,
            "alert_code": alert.alert_code,
            "zone_id": alert.zone_id,
            "zone_name": alert.zone.name if alert.zone else f"Zone {alert.zone_id}",
            "risk_tier": alert.risk_tier,
            "hazard_type": alert.hazard_type,
            "message": alert.message,
            "affected_workers_count": alert.affected_workers_count,
            "route_details": alert.route_details,
            "is_active": True,
            "created_at": alert.created_at.isoformat(),
        },
    )

    return EmergencyAlertResponse(
        id=alert.id,
        alert_code=alert.alert_code,
        zone_id=alert.zone_id,
        zone_name=alert.zone.name if alert.zone else f"Zone {alert.zone_id}",
        risk_tier=alert.risk_tier,
        hazard_type=alert.hazard_type,
        message=alert.message,
        affected_workers_count=alert.affected_workers_count,
        acknowledged_count=alert.acknowledged_count,
        evacuated_safe_count=alert.evacuated_safe_count,
        trapped_count=alert.trapped_count,
        is_active=alert.is_active,
        route_details=alert.route_details,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
    )


@router.post("/{alert_id}/acknowledge", status_code=status.HTTP_200_OK)
async def acknowledge_evacuation(
    alert_id: int,
    ack_in: EmergencyAlertAck,
    db: Session = Depends(get_db),
):
    """
    Process 2-way status feedback from a worker or field supervisor:
    Status options: 'acknowledged', 'evacuating', 'safe', 'trapped'.
    """
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert ID {alert_id} not found.")

    worker = db.query(Worker).filter(Worker.id == ack_in.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker ID {ack_in.worker_id} not found.")

    evac_status = process_worker_acknowledgement(
        db=db,
        alert_id=alert_id,
        worker_id=ack_in.worker_id,
        status=ack_in.status,
        notes=ack_in.notes,
    )

    db.refresh(alert)

    # Broadcast EVACUATION_STATUS update via WebSockets
    await ws_manager.broadcast(
        event_type="EVACUATION_STATUS",
        data={
            "alert_id": alert.id,
            "worker_id": worker.id,
            "worker_code": worker.worker_code,
            "worker_name": worker.full_name,
            "status": evac_status.status,
            "affected_workers_count": alert.affected_workers_count,
            "acknowledged_count": alert.acknowledged_count,
            "evacuated_safe_count": alert.evacuated_safe_count,
            "trapped_count": alert.trapped_count,
            "last_updated": evac_status.last_updated.isoformat(),
        },
    )

    return {
        "status": "success",
        "alert_id": alert.id,
        "worker_id": worker.id,
        "worker_status": evac_status.status,
        "acknowledged_count": alert.acknowledged_count,
        "evacuated_safe_count": alert.evacuated_safe_count,
        "trapped_count": alert.trapped_count,
    }


@router.get("/{alert_id}/evacuation-status", response_model=AlertEvacuationStatusSummary)
def get_alert_evacuation_status(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed real-time evacuation roster for an emergency alert."""
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert ID {alert_id} not found.")

    statuses = db.query(WorkerEvacuationStatus).filter(WorkerEvacuationStatus.alert_id == alert_id).all()
    worker_details = []
    for s in statuses:
        w = s.worker
        worker_details.append(
            WorkerEvacuationDetail(
                worker_id=w.id,
                worker_code=w.worker_code,
                full_name=w.full_name,
                role=w.role,
                phone=w.phone,
                status=s.status,
                acknowledged_at=s.acknowledged_at,
                safe_at=s.safe_at,
                last_updated=s.last_updated,
            )
        )

    pending_ack = max(0, alert.affected_workers_count - alert.acknowledged_count)

    return AlertEvacuationStatusSummary(
        alert_id=alert.id,
        alert_code=alert.alert_code,
        zone_id=alert.zone_id,
        zone_name=alert.zone.name if alert.zone else f"Zone {alert.zone_id}",
        risk_tier=alert.risk_tier,
        hazard_type=alert.hazard_type,
        is_active=alert.is_active,
        affected_workers_count=alert.affected_workers_count,
        acknowledged_count=alert.acknowledged_count,
        evacuated_safe_count=alert.evacuated_safe_count,
        trapped_count=alert.trapped_count,
        pending_ack_count=pending_ack,
        route_details=alert.route_details,
        workers=worker_details,
    )


@router.post("/{alert_id}/resolve", response_model=EmergencyAlertResponse)
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolves an active emergency alert, resetting worker statuses back to active."""
    try:
        alert = resolve_emergency_alert(db=db, alert_id=alert_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    await ws_manager.broadcast(
        event_type="EMERGENCY_ALERT_RESOLVED",
        data={
            "alert_id": alert.id,
            "alert_code": alert.alert_code,
            "zone_id": alert.zone_id,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        },
    )

    return EmergencyAlertResponse(
        id=alert.id,
        alert_code=alert.alert_code,
        zone_id=alert.zone_id,
        zone_name=alert.zone.name if alert.zone else f"Zone {alert.zone_id}",
        risk_tier=alert.risk_tier,
        hazard_type=alert.hazard_type,
        message=alert.message,
        affected_workers_count=alert.affected_workers_count,
        acknowledged_count=alert.acknowledged_count,
        evacuated_safe_count=alert.evacuated_safe_count,
        trapped_count=alert.trapped_count,
        is_active=alert.is_active,
        route_details=alert.route_details,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
    )
