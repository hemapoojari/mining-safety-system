"""
Targeted Emergency Alert Dispatcher & Evacuation Tracker Service
Coordinates emergency creation, targeted worker dispatch, two-way worker acknowledgements,
and real-time evacuation tallies.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.database.models import (
    EmergencyAlert,
    WorkerEvacuationStatus,
    Worker,
    MiningZone,
)
from backend.app.services.evacuation_routing import calculate_evacuation_route


def generate_alert_code() -> str:
    """Generates a human-readable unique alert code, e.g., EVAC-A8F2."""
    return f"EVAC-{uuid.uuid4().hex[:6].upper()}"


def trigger_emergency_evacuation(
    db: Session,
    zone_id: int,
    risk_tier: str,
    hazard_type: str,
    message: str,
) -> EmergencyAlert:
    """
    Creates an EmergencyAlert, queries all workers in the affected zone,
    calculates verified evacuation routes to safe refuge points,
    and initializes targeted evacuation records for each worker.
    """
    zone = db.query(MiningZone).filter(MiningZone.id == zone_id).first()
    if not zone:
        raise ValueError(f"Mining zone ID {zone_id} does not exist.")

    # 1. Compute Evacuation Route to Designated Safe Refuge Station
    route_info = calculate_evacuation_route(zone_id)
    enhanced_message = message
    if route_info.get("instructions"):
        enhanced_message = f"{message} | {route_info['instructions']}"

    # 2. Create Emergency Alert Record
    alert = EmergencyAlert(
        alert_code=generate_alert_code(),
        zone_id=zone_id,
        risk_tier=risk_tier,
        hazard_type=hazard_type,
        message=enhanced_message,
        route_details=json.dumps(route_info),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.flush()  # Populates alert.id

    # 3. Find all workers currently localized or assigned to this zone
    affected_workers = db.query(Worker).filter(Worker.zone_id == zone_id).all()
    
    # 4. Create targeted worker evacuation records (Status: Alert Sent / notified)
    for worker in affected_workers:
        status_rec = WorkerEvacuationStatus(
            alert_id=alert.id,
            worker_id=worker.id,
            status="notified",  # Alert Sent
            last_updated=datetime.now(timezone.utc),
        )
        db.add(status_rec)
        # Mark worker status as alerted / notified (not safe until confirmed at refuge)
        worker.status = "evacuating" if risk_tier == "Critical" else "active"

    # Update counts on alert
    alert.affected_workers_count = len(affected_workers)
    alert.acknowledged_count = 0
    alert.evacuated_safe_count = 0
    alert.trapped_count = 0

    # Escalate zone risk tier if not already matching
    if zone.current_risk_tier != risk_tier:
        zone.current_risk_tier = risk_tier
        zone.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alert)
    return alert


def normalize_status(raw_status: str) -> str:
    """Normalizes UI and user-facing status strings to canonical database keys."""
    s = raw_status.strip().lower()
    if s in ["notified", "alert sent", "alert_sent"]:
        return "notified"
    if s in ["acknowledged", "ack"]:
        return "acknowledged"
    if s in ["evacuating", "in_transit"]:
        return "evacuating"
    if s in ["safe", "reached safe zone", "reached_safe_zone"]:
        return "safe"
    if s in ["trapped", "need assistance"]:
        return "trapped"
    return s


def process_worker_acknowledgement(
    db: Session,
    alert_id: int,
    worker_id: int,
    status: str,  # "acknowledged", "evacuating", "safe", "trapped"
    notes: Optional[str] = None,
) -> WorkerEvacuationStatus:
    """
    Processes 2-way status feedback from a worker companion client or supervisor.
    Enforces strict safety logic: Acknowledgement confirms receipt, but only
    'safe' / 'Reached Safe Zone' marks the worker as safe.
    """
    canonical_status = normalize_status(status)
    evac_status = (
        db.query(WorkerEvacuationStatus)
        .filter(
            WorkerEvacuationStatus.alert_id == alert_id,
            WorkerEvacuationStatus.worker_id == worker_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if not evac_status:
        # If worker entered zone after alert creation, register them dynamically
        evac_status = WorkerEvacuationStatus(
            alert_id=alert_id,
            worker_id=worker_id,
            status=canonical_status,
            notes=notes,
            last_updated=now,
        )
        db.add(evac_status)
    else:
        evac_status.status = canonical_status
        evac_status.notes = notes
        evac_status.last_updated = now

    if canonical_status in ["acknowledged", "evacuating"]:
        if not evac_status.acknowledged_at:
            evac_status.acknowledged_at = now
    elif canonical_status == "safe":
        if not evac_status.acknowledged_at:
            evac_status.acknowledged_at = now
        evac_status.safe_at = now

    # Also sync worker's main record
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if worker:
        worker.status = canonical_status
        worker.last_ping = now

    db.flush()

    # Recalculate tallies for the alert
    all_statuses = db.query(WorkerEvacuationStatus).filter(WorkerEvacuationStatus.alert_id == alert_id).all()
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if alert:
        alert.affected_workers_count = len(all_statuses)
        alert.acknowledged_count = sum(1 for s in all_statuses if s.status in ["acknowledged", "evacuating", "safe", "trapped"])
        alert.evacuated_safe_count = sum(1 for s in all_statuses if s.status == "safe")
        alert.trapped_count = sum(1 for s in all_statuses if s.status == "trapped")

    db.commit()
    db.refresh(evac_status)
    return evac_status


def resolve_emergency_alert(db: Session, alert_id: int) -> EmergencyAlert:
    """Marks an active emergency alert as resolved and normalizes worker states."""
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if not alert:
        raise ValueError(f"Alert ID {alert_id} not found.")

    alert.is_active = False
    alert.resolved_at = datetime.now(timezone.utc)

    # Re-evaluate zone risk back to Safe if no other active alerts remain
    other_alerts = db.query(EmergencyAlert).filter(
        EmergencyAlert.zone_id == alert.zone_id,
        EmergencyAlert.is_active == True,
        EmergencyAlert.id != alert.id,
    ).count()

    if other_alerts == 0:
        zone = db.query(MiningZone).filter(MiningZone.id == alert.zone_id).first()
        if zone:
            zone.current_risk_tier = "Safe"
            zone.updated_at = datetime.now(timezone.utc)

    # Reset worker statuses in that zone back to active if they were safe/evacuating
    evac_statuses = db.query(WorkerEvacuationStatus).filter(WorkerEvacuationStatus.alert_id == alert_id).all()
    for s in evac_statuses:
        worker = db.query(Worker).filter(Worker.id == s.worker_id).first()
        if worker and worker.status in ["safe", "evacuating"]:
            worker.status = "active"

    db.commit()
    db.refresh(alert)
    return alert
