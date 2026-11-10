"""
Statutory Reports & File Export Router
AI/ML-Powered Mining Safety and Worker Evacuation System

Provides endpoints for downloading:
1. Official Multi-Page PDF Incident & Evacuation Audit Reports
2. Comprehensive PDF Zone Safety Summaries
3. CSV Historical Sensor Telemetry Datasets
4. CSV Emergency Incidents & Evacuation Ledgers
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.database.models import EmergencyAlert, MiningZone, SensorReading
from backend.app.services.report_generator import (
    generate_incident_pdf,
    generate_zone_safety_pdf,
    generate_sensor_csv,
    generate_incidents_csv,
)

logger = logging.getLogger("mining_safety.reports")

router = APIRouter(prefix="/api/reports", tags=["Statutory Reports & Data Exports"])


@router.get("/incident/{alert_id}/pdf", status_code=status.HTTP_200_OK)
def download_incident_pdf(alert_id: int, db: Session = Depends(get_db)):
    """
    Generates and downloads an official multi-page PDF Incident Audit Report
    for a specific emergency alert record.
    """
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency Alert ID {alert_id} not found.",
        )

    try:
        pdf_bytes = generate_incident_pdf(alert, db)
    except Exception as e:
        logger.error(f"Failed to generate incident PDF for alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile PDF report: {e}",
        )

    filename = f"Incident_Audit_{alert.alert_code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/zone/{zone_id}/pdf", status_code=status.HTTP_200_OK)
def download_zone_safety_pdf(zone_id: int, db: Session = Depends(get_db)):
    """
    Generates and downloads an official PDF Sector Safety Summary
    for a specific mining zone.
    """
    zone = db.query(MiningZone).filter(MiningZone.id == zone_id).first()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mining Zone ID {zone_id} not found.",
        )

    try:
        pdf_bytes = generate_zone_safety_pdf(zone, db)
    except Exception as e:
        logger.error(f"Failed to generate zone safety PDF for zone {zone_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile zone safety PDF: {e}",
        )

    filename = f"Zone_Safety_Summary_{zone.zone_code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/sensors/csv", status_code=status.HTTP_200_OK)
def download_sensors_csv(
    zone_id: Optional[int] = Query(None, description="Filter by mining zone ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor parameter"),
    mine_type: Optional[str] = Query(None, pattern="^(open_pit|underground)$"),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """
    Generates and downloads a standard CSV telemetry dataset of historical sensor readings.
    """
    query = db.query(SensorReading).order_by(desc(SensorReading.timestamp))

    if zone_id is not None:
        query = query.filter(SensorReading.zone_id == zone_id)
    if sensor_type:
        query = query.filter(SensorReading.sensor_type == sensor_type)
    if mine_type:
        query = query.filter(SensorReading.mine_type == mine_type)

    readings = query.limit(limit).all()
    zone_map = {z.id: z for z in db.query(MiningZone).all()}

    csv_data = generate_sensor_csv(readings, zone_map)
    filename = "historical_sensor_telemetry.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/incidents/csv", status_code=status.HTTP_200_OK)
def download_incidents_csv(db: Session = Depends(get_db)):
    """
    Generates and downloads a standard CSV emergency incidents and evacuation performance ledger.
    """
    alerts = db.query(EmergencyAlert).order_by(desc(EmergencyAlert.created_at)).all()
    zone_map = {z.id: z for z in db.query(MiningZone).all()}

    csv_data = generate_incidents_csv(alerts, zone_map)
    filename = "emergency_incidents_evacuation_ledger.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
