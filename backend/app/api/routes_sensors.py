"""
Sensor Telemetry Endpoints
Handles sensor registry, ingestion of real/simulated readings, current values, and time-series history.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.database.models import Sensor, SensorReading, MiningZone, RiskPrediction
from backend.app.schemas.sensor_schema import (
    SensorResponse,
    SensorCreate,
    SensorReadingResponse,
    SensorReadingCreate,
    CurrentSensorReadingResponse,
    ZoneTelemetrySummary,
)
from backend.app.services.risk_engine import assess_zone_risk
from backend.app.services.alert_service import trigger_emergency_evacuation
from backend.app.api.websocket import ws_manager

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


# -------------------------------------------------------------
# 1. SENSOR INVENTORY / REGISTRY
# -------------------------------------------------------------

@router.get("", response_model=List[SensorResponse], include_in_schema=False)
@router.get("/", response_model=List[SensorResponse])
def get_sensors(
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    mine_type: Optional[str] = Query(None, description="Filter by open_pit or underground"),
    db: Session = Depends(get_db),
):
    """Retrieve all registered sensors in the mine with optional filtering."""
    query = db.query(Sensor)
    if zone_id:
        query = query.filter(Sensor.zone_id == zone_id)
    if mine_type:
        query = query.filter(Sensor.mine_type == mine_type)
    return query.all()


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def register_sensor(
    sensor_in: SensorCreate,
    db: Session = Depends(get_db),
):
    """Register a new sensor into a designated mining zone."""
    zone = db.query(MiningZone).filter(MiningZone.id == sensor_in.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone ID {sensor_in.zone_id} not found.")

    existing = db.query(Sensor).filter(Sensor.sensor_code == sensor_in.sensor_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Sensor code {sensor_in.sensor_code} already registered.")

    sensor = Sensor(
        sensor_code=sensor_in.sensor_code,
        name=sensor_in.name,
        zone_id=sensor_in.zone_id,
        mine_type=sensor_in.mine_type,
        sensor_type=sensor_in.sensor_type,
        unit=sensor_in.unit,
        status=sensor_in.status,
        installed_at=datetime.now(timezone.utc),
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


# -------------------------------------------------------------
# 2. SENSOR TELEMETRY INGESTION (REAL OR SIMULATED)
# -------------------------------------------------------------

@router.post("/readings", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def submit_sensor_reading(
    reading_in: SensorReadingCreate,
    db: Session = Depends(get_db),
):
    """
    Ingest a new real or simulated sensor reading.
    Triggers automated zone risk assessment and broadcasts telemetry via WebSockets.
    """
    zone = db.query(MiningZone).filter(MiningZone.id == reading_in.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone ID {reading_in.zone_id} not found.")

    # Match sensor id if available
    sensor = db.query(Sensor).filter(Sensor.sensor_code == reading_in.sensor_code).first()
    sensor_id = sensor.id if sensor else reading_in.sensor_id

    # Create Reading Record
    reading = SensorReading(
        sensor_id=sensor_id,
        sensor_code=reading_in.sensor_code,
        zone_id=reading_in.zone_id,
        mine_type=reading_in.mine_type,
        sensor_type=reading_in.sensor_type,
        value=reading_in.value,
        unit=reading_in.unit,
        timestamp=reading_in.timestamp or datetime.now(timezone.utc),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # 1. Fetch latest readings for all sensors in this zone for holistic evaluation
    latest_readings_subquery = (
        db.query(SensorReading.sensor_type, SensorReading.value)
        .filter(SensorReading.zone_id == reading_in.zone_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(20)
        .all()
    )
    snapshot = {}
    for stype, sval in latest_readings_subquery:
        if stype not in snapshot:
            snapshot[stype] = sval
    snapshot[reading_in.sensor_type] = reading_in.value

    # 2. Execute centralized risk evaluation
    risk_eval = assess_zone_risk(zone.mine_type, snapshot)
    new_tier = risk_eval["risk_tier"]
    composite_score = risk_eval["composite_score"]
    dominant_hazard = risk_eval["dominant_hazard"]

    # 3. Store Risk Prediction record
    pred = RiskPrediction(
        zone_id=zone.id,
        mine_type=zone.mine_type,
        hazard_type=dominant_hazard,
        risk_score=composite_score,
        risk_tier=new_tier,
        confidence=risk_eval.get("confidence", 0.95),
        model_name=risk_eval.get("model_name", "ML_Ensemble"),
        calculation_method=risk_eval.get("calculation_method", "ml_model_with_threshold_safeguard"),
        details=str(risk_eval["breakdown"]),
        timestamp=datetime.now(timezone.utc),
    )
    db.add(pred)

    # 4. Update Zone Risk status
    prev_tier = zone.current_risk_tier
    zone.current_risk_tier = new_tier
    zone.updated_at = datetime.now(timezone.utc)
    db.commit()

    # 5. Broadcast SENSOR_READING event via WebSocket
    await ws_manager.broadcast(
        event_type="SENSOR_READING",
        data={
            "sensor_code": reading.sensor_code,
            "zone_id": reading.zone_id,
            "zone_name": zone.name,
            "mine_type": reading.mine_type,
            "sensor_type": reading.sensor_type,
            "value": reading.value,
            "unit": reading.unit,
            "timestamp": reading.timestamp.isoformat(),
        },
    )

    # 6. Broadcast RISK_UPDATE event via WebSocket with ML prediction details
    await ws_manager.broadcast(
        event_type="RISK_UPDATE",
        data={
            "zone_id": zone.id,
            "zone_name": zone.name,
            "mine_type": zone.mine_type,
            "previous_risk_tier": prev_tier,
            "current_risk_tier": new_tier,
            "composite_score": composite_score,
            "dominant_hazard": dominant_hazard,
            "model_name": risk_eval.get("model_name"),
            "confidence": risk_eval.get("confidence"),
            "breakdown": risk_eval["breakdown"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # 7. Auto-escalate to Emergency Alert if Critical risk reached and no active alert
    if new_tier == "Critical":
        from backend.app.database.models import EmergencyAlert
        active_alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.zone_id == zone.id,
            EmergencyAlert.is_active == True,
        ).first()
        if not active_alert:
            alert = trigger_emergency_evacuation(
                db=db,
                zone_id=zone.id,
                risk_tier="Critical",
                hazard_type=dominant_hazard,
                message=f"CRITICAL HAZARD: Automated detection of dangerous {dominant_hazard} in {zone.name}. Immediate evacuation required.",
            )
            await ws_manager.broadcast(
                event_type="EMERGENCY_ALERT",
                data={
                    "alert_id": alert.id,
                    "alert_code": alert.alert_code,
                    "zone_id": zone.id,
                    "zone_name": zone.name,
                    "risk_tier": alert.risk_tier,
                    "hazard_type": alert.hazard_type,
                    "message": alert.message,
                    "affected_workers_count": alert.affected_workers_count,
                    "route_details": alert.route_details,
                    "is_active": True,
                    "created_at": alert.created_at.isoformat(),
                },
            )

    return reading


# -------------------------------------------------------------
# 3. CURRENT READINGS & HISTORICAL TIME-SERIES
# -------------------------------------------------------------

@router.get("/readings/current", response_model=List[CurrentSensorReadingResponse])
def get_current_sensor_readings(
    zone_id: Optional[int] = Query(None, description="Optional zone filter"),
    db: Session = Depends(get_db),
):
    """Retrieve the latest real-time reading for each sensor."""
    sensors_query = db.query(Sensor)
    if zone_id:
        sensors_query = sensors_query.filter(Sensor.zone_id == zone_id)
    sensors = sensors_query.all()

    results = []
    for s in sensors:
        latest = (
            db.query(SensorReading)
            .filter(SensorReading.sensor_code == s.sensor_code)
            .order_by(desc(SensorReading.timestamp))
            .first()
        )
        zone = db.query(MiningZone).filter(MiningZone.id == s.zone_id).first()
        zone_name = zone.name if zone else f"Zone {s.zone_id}"
        
        results.append(
            CurrentSensorReadingResponse(
                sensor_code=s.sensor_code,
                name=s.name,
                zone_id=s.zone_id,
                zone_name=zone_name,
                mine_type=s.mine_type,
                sensor_type=s.sensor_type,
                latest_value=latest.value if latest else 0.0,
                unit=s.unit,
                status=s.status,
                last_updated=latest.timestamp if latest else s.installed_at,
            )
        )
    return results


@router.get("/readings/history", response_model=List[SensorReadingResponse])
def get_sensor_history(
    zone_id: Optional[int] = Query(None),
    sensor_type: Optional[str] = Query(None),
    sensor_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Query historical time-series sensor telemetry."""
    query = db.query(SensorReading)
    if zone_id:
        query = query.filter(SensorReading.zone_id == zone_id)
    if sensor_type:
        query = query.filter(SensorReading.sensor_type == sensor_type)
    if sensor_code:
        query = query.filter(SensorReading.sensor_code == sensor_code)
    
    return query.order_by(desc(SensorReading.timestamp)).limit(limit).all()


# -------------------------------------------------------------
# 4. SIMULATION TELEMETRY TICK (ACADEMIC DEMO GENERATOR)
# -------------------------------------------------------------

@router.post("/simulate-tick")
async def simulate_telemetry_tick(
    anomaly: Optional[str] = Query(None, description="Inject anomaly scenario: 'gas_leak', 'rockfall', 'thermal_runaway'"),
    db: Session = Depends(get_db),
):
    """
    Triggers one cycle of simulated sensor readings across all mining zones.
    Useful for demonstration and automated real-time stream simulation.
    """
    from simulation.sensor_simulator import SensorSimulator

    simulator = SensorSimulator()
    if anomaly:
        simulator.trigger_anomaly(anomaly)

    zones = db.query(MiningZone).all()
    generated_readings = []

    for zone in zones:
        if zone.mine_type == "open_pit":
            readings = simulator.generate_open_pit_reading(zone.id)
        else:
            readings = simulator.generate_underground_reading(zone.id)

        for r_dict in readings:
            r_in = SensorReadingCreate(**r_dict)
            saved = await submit_sensor_reading(r_in, db)
            generated_readings.append(saved.sensor_code)

    return {
        "status": "success",
        "anomaly_injected": anomaly or "none",
        "readings_generated": len(generated_readings),
        "zones_processed": len(zones),
    }

