"""
Simulation Engine Control & Automated Ingestion Stream Router
Provides unified REST controls for starting/stopping background simulation loops,
injecting hazard scenarios, resetting state, and manual single-tick execution.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db, SessionLocal
from backend.app.database.models import MiningZone, Worker, SensorReading, EmergencyAlert, WorkerEvacuationStatus
from backend.app.schemas.sensor_schema import SensorReadingCreate
from backend.app.api.routes_sensors import submit_sensor_reading
from backend.app.services.alert_service import process_worker_acknowledgement, resolve_emergency_alert
from backend.app.services.geofence_service import resolve_zone_for_coordinates
from backend.app.api.websocket import ws_manager
from simulation.sensor_simulator import SensorSimulator
from simulation.worker_simulator import WorkerSimulator

logger = logging.getLogger("mining_safety.simulation")

router = APIRouter(prefix="/api/simulation", tags=["Simulation Control"])

# Singleton simulation engines
sensor_sim = SensorSimulator()
worker_sim = WorkerSimulator()

# Global background loop reference
_bg_task: Optional[asyncio.Task] = None
_bg_running: bool = False
_tick_interval_seconds: float = 3.5


class ScenarioRequest(BaseModel):
    scenario: str = Field(..., pattern="^(normal|progressive_drift|open_pit_hazard|gas_leak|fire_hazard)$")


class SimulationStatusResponse(BaseModel):
    is_running: bool
    current_scenario: str
    tick_count: int
    scenario_tick: int
    active_alerts_count: int
    interval_seconds: float


@router.get("/status", response_model=SimulationStatusResponse)
def get_simulation_status(db: Session = Depends(get_db)):
    """Returns current state of the real-time simulation engine."""
    active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True).count()
    return SimulationStatusResponse(
        is_running=_bg_running,
        current_scenario=sensor_sim.current_scenario,
        tick_count=sensor_sim.tick_count,
        scenario_tick=sensor_sim.scenario_tick,
        active_alerts_count=active_alerts,
        interval_seconds=_tick_interval_seconds,
    )


async def execute_simulation_cycle(db: Session) -> Dict[str, Any]:
    """
    Executes one discrete simulation step:
    1. Generates 6-feature sensor readings across all 6 zones.
    2. Runs dual-engine ML prediction & statutory threshold safeguards.
    3. Triggers automated emergency alerts on Critical escalation.
    4. Simulates natural worker movement and active evacuation progression.
    5. Broadcasts real-time events via WebSockets.
    """
    zones = db.query(MiningZone).all()
    workers = db.query(Worker).all()
    active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True).all()
    alert_zone_ids = {a.zone_id: a for a in active_alerts}

    # 1. Step Sensor Telemetry & Predictions
    readings_count = 0
    for zone in zones:
        if zone.mine_type == "open_pit":
            readings = sensor_sim.generate_open_pit_reading(zone.id)
        else:
            readings = sensor_sim.generate_underground_reading(zone.id)

        for r_dict in readings:
            r_in = SensorReadingCreate(**r_dict)
            await submit_sensor_reading(r_in, db)
            readings_count += 1

    # 2. Step Worker Movement & Evacuation Trajectory
    moved_workers = 0
    for worker in workers:
        is_in_hazard = worker.zone_id in alert_zone_ids
        active_alert = alert_zone_ids.get(worker.zone_id)
        is_evac = is_in_hazard and active_alert is not None

        dest_coords = None
        if is_evac:
            dest_coords = worker_sim.get_zone_destination(worker.zone_id)

        w_dict = {
            "current_lat": worker.current_lat,
            "current_lng": worker.current_lng,
            "status": worker.status,
        }
        stepped = worker_sim.step_worker_position(
            w_dict,
            is_evacuating=is_evac,
            evac_destination=dest_coords,
        )

        worker.current_lat = stepped["current_lat"]
        worker.current_lng = stepped["current_lng"]
        prev_status = worker.status
        new_status = stepped["status"]
        worker.status = new_status
        worker.last_ping = datetime.now(timezone.utc)

        # If worker arrived at refuge station during evacuation, record 2-way safe status
        if is_evac and new_status == "safe" and prev_status != "safe":
            process_worker_acknowledgement(
                db=db,
                alert_id=active_alert.id,
                worker_id=worker.id,
                status="safe",  # Reached Safe Zone
                notes="Automated simulation: Worker arrived safely at designated refuge chamber",
            )
            await ws_manager.broadcast(
                event_type="EVACUATION_STATUS",
                data={
                    "alert_id": active_alert.id,
                    "worker_id": worker.id,
                    "worker_code": worker.worker_code,
                    "worker_name": worker.full_name,
                    "status": "safe",
                    "affected_workers_count": active_alert.affected_workers_count,
                    "acknowledged_count": active_alert.acknowledged_count,
                    "evacuated_safe_count": active_alert.evacuated_safe_count,
                    "trapped_count": active_alert.trapped_count,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                },
            )

        # Broadcast worker location update
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
                "zone_name": worker.zone.name if worker.zone else "Unassigned",
                "status": worker.status,
                "last_ping": worker.last_ping.isoformat(),
                "is_simulated": True,
            },
        )
        moved_workers += 1

    db.commit()

    # Advance simulator internal clock
    sensor_sim.step()

    # Broadcast simulation state event
    await ws_manager.broadcast(
        event_type="SIMULATION_STATE",
        data={
            "is_running": _bg_running,
            "current_scenario": sensor_sim.current_scenario,
            "tick_count": sensor_sim.tick_count,
            "scenario_tick": sensor_sim.scenario_tick,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {
        "status": "success",
        "scenario": sensor_sim.current_scenario,
        "tick_count": sensor_sim.tick_count,
        "readings_generated": readings_count,
        "workers_updated": moved_workers,
    }


async def _background_simulation_runner():
    """Continuous async loop executing simulation ticks."""
    global _bg_running
    logger.info("Starting background real-time simulation runner...")
    while _bg_running:
        try:
            with SessionLocal() as db:
                await execute_simulation_cycle(db)
        except Exception as e:
            logger.error(f"Error in simulation cycle: {e}", exc_info=True)
        await asyncio.sleep(_tick_interval_seconds)
    logger.info("Background simulation runner stopped.")


@router.post("/start")
async def start_simulation():
    """Starts the real-time simulation background loop."""
    global _bg_task, _bg_running
    if _bg_running:
        return {"status": "already_running", "scenario": sensor_sim.current_scenario}

    _bg_running = True
    sensor_sim.start()
    _bg_task = asyncio.create_task(_background_simulation_runner())
    return {
        "status": "started",
        "scenario": sensor_sim.current_scenario,
        "interval_seconds": _tick_interval_seconds,
    }


@router.post("/stop")
async def stop_simulation():
    """Pauses the real-time simulation background loop."""
    global _bg_task, _bg_running
    _bg_running = False
    sensor_sim.stop()
    if _bg_task:
        _bg_task.cancel()
        _bg_task = None
    return {"status": "stopped", "tick_count": sensor_sim.tick_count}


@router.post("/scenario")
async def set_scenario(req: ScenarioRequest):
    """
    Sets active simulation scenario:
    - 'normal'
    - 'progressive_drift'
    - 'open_pit_hazard'
    - 'gas_leak'
    - 'fire_hazard'
    """
    sensor_sim.set_scenario(req.scenario)
    return {
        "status": "scenario_updated",
        "scenario": sensor_sim.current_scenario,
        "message": f"Active simulation scenario changed to '{req.scenario}'",
    }


@router.post("/tick")
async def manual_simulation_tick(db: Session = Depends(get_db)):
    """Executes a single discrete simulation tick immediately."""
    result = await execute_simulation_cycle(db)
    return result


@router.post("/reset")
async def reset_simulation(db: Session = Depends(get_db)):
    """
    Resets simulation back to normal baseline:
    - Sets scenario to 'normal'
    - Resolves all active emergency alerts
    - Normalizes zone risk levels to Safe
    - Resets worker status to active and returns coordinates to baseline
    """
    sensor_sim.reset()

    # Resolve all active alerts
    active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.is_active == True).all()
    for alert in active_alerts:
        resolve_emergency_alert(db, alert.id)

    # Normalize zones
    zones = db.query(MiningZone).all()
    for z in zones:
        z.current_risk_tier = "Safe"
        z.updated_at = datetime.now(timezone.utc)

    # Reset workers
    workers = db.query(Worker).all()
    for w in workers:
        w.status = "active"

    db.commit()

    await ws_manager.broadcast(
        event_type="SIMULATION_STATE",
        data={
            "is_running": _bg_running,
            "current_scenario": "normal",
            "tick_count": 0,
            "scenario_tick": 0,
            "message": "Simulation reset to nominal baseline",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {
        "status": "reset_complete",
        "current_scenario": "normal",
        "active_alerts_cleared": len(active_alerts),
    }
