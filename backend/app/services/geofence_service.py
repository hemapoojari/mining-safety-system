"""
Worker Geofencing & Spatial Zone Mapping Service
Maps worker coordinates (GPS/indoor positioning) to 2D/3D mine zones
and identifies workers currently residing within hazard zones.
"""
import json
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.database.models import Worker, MiningZone


def is_point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """
    Ray-casting algorithm for 2D Point-in-Polygon testing.
    point: (lat, lng)
    polygon: [[lat1, lng1], [lat2, lng2], ...]
    """
    if not polygon or len(polygon) < 3:
        return False

    lat, lng = point
    n = len(polygon)
    inside = False

    p1_lat, p1_lng = polygon[0]
    for i in range(n + 1):
        p2_lat, p2_lng = polygon[i % n]
        if lng > min(p1_lng, p2_lng):
            if lng <= max(p1_lng, p2_lng):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lng != p2_lng:
                        xinters = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat
                    else:
                        xinters = p1_lat
                    if p1_lat == p2_lat or lat <= xinters:
                        inside = not inside
        p1_lat, p1_lng = p2_lat, p2_lng

    return inside


def resolve_zone_for_coordinates(
    lat: float,
    lng: float,
    zones: List[MiningZone],
) -> Optional[MiningZone]:
    """
    Given worker coordinates, tests against all zone boundary polygons to find matching zone.
    """
    for zone in zones:
        if not zone.boundary_geo:
            continue
        try:
            poly = json.loads(zone.boundary_geo)
            if is_point_in_polygon((lat, lng), poly):
                return zone
        except Exception:
            continue
    return None


def get_workers_in_zone(db: Session, zone_id: int) -> List[Worker]:
    """Retrieve all workers currently assigned or localized in a given zone."""
    return db.query(Worker).filter(Worker.zone_id == zone_id).all()


def get_workers_in_hazard_zones(db: Session, hazard_zone_ids: List[int]) -> List[Worker]:
    """Retrieve all workers located inside any designated hazard zones."""
    if not hazard_zone_ids:
        return []
    return db.query(Worker).filter(Worker.zone_id.in_(hazard_zone_ids)).all()
