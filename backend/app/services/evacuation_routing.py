"""
Evacuation Routing & Safe Refuge Station Service
Calculates verified geometric evacuation paths from hazardous mining zones
to designated surface muster stations and underground fresh-air refuge chambers.

Safety Rules:
- Evacuation corridors must avoid passing through active Critical hazard zones.
- If a route is blocked by fire, toxic gas, or rockfall debris, flags 'UNSAFE_BLOCKED'
  and instructs workers to shelter in place behind hermetic seals.
- Never invents routes through unmapped or hazardous corridors.
"""
import math
from typing import Dict, Any, List, Optional, Tuple

# Pre-configured Safe Refuge Destinations
SAFE_REFUGE_POINTS = {
    "open_pit": {
        "id": "REFUGE-SURFACE-01",
        "name": "North Pit Surface Muster Station",
        "type": "surface_muster",
        "coordinates": [23.7480, 86.4160],
        "capacity": 100,
        "description": "Safe open-air assembly ground above pit crest outside kinematic runout limits.",
    },
    "underground": {
        "id": "REFUGE-CHAMBER-01",
        "name": "Underground Fresh-Air Refuge Chamber #1",
        "type": "hermetic_refuge_chamber",
        "coordinates": [23.7428, 86.4122],
        "capacity": 30,
        "description": "Positive-pressure sealed steel chamber with 48h oxygen, CO2 scrubbers, and water.",
    },
    "underground_portal": {
        "id": "PORTAL-MAIN-01",
        "name": "Main Incline Drift Portal (Surface Adit)",
        "type": "mine_portal",
        "coordinates": [23.7445, 86.4145],
        "capacity": 200,
        "description": "Fresh-air intake drift exit connecting directly to surface ground.",
    },
}

# Pre-surveyed Mine Corridors (Zone centroid/entrance -> Refuge Station)
CORRIDORS = {
    # Open-Pit Zones -> Surface Muster
    1: {  # OP-Z1 (Upper Wall)
        "destination": SAFE_REFUGE_POINTS["open_pit"],
        "waypoints": [
            [23.7462, 86.4152],
            [23.7472, 86.4158],
            [23.7480, 86.4160],
        ],
        "traverses_zones": [1],
    },
    2: {  # OP-Z2 (East Highwall)
        "destination": SAFE_REFUGE_POINTS["open_pit"],
        "waypoints": [
            [23.7452, 86.4182],
            [23.7468, 86.4172],
            [23.7480, 86.4160],
        ],
        "traverses_zones": [2],
    },
    3: {  # OP-Z3 (Haulage Ramp)
        "destination": SAFE_REFUGE_POINTS["open_pit"],
        "waypoints": [
            [23.7438, 86.4148],
            [23.7458, 86.4152],
            [23.7472, 86.4158],
            [23.7480, 86.4160],
        ],
        "traverses_zones": [3, 1],
    },
    # Underground Zones -> Fresh-Air Refuge Chamber #1
    4: {  # UG-Z1 (Shaft #2 Level -150m)
        "destination": SAFE_REFUGE_POINTS["underground"],
        "waypoints": [
            [23.7422, 86.4128],
            [23.7425, 86.4125],
            [23.7428, 86.4122],
        ],
        "traverses_zones": [4],
    },
    5: {  # UG-Z2 (Sub-Level Stope C)
        "destination": SAFE_REFUGE_POINTS["underground"],
        "waypoints": [
            [23.7412, 86.4138],
            [23.7420, 86.4130],
            [23.7425, 86.4125],
            [23.7428, 86.4122],
        ],
        "traverses_zones": [5, 4],
    },
    6: {  # UG-Z3 (South Return Airway)
        "destination": SAFE_REFUGE_POINTS["underground"],
        "waypoints": [
            [23.7402, 86.4148],
            [23.7412, 86.4138],
            [23.7420, 86.4130],
            [23.7428, 86.4122],
        ],
        "traverses_zones": [6, 5, 4],
    },
}


def haversine_distance_meters(coord1: List[float], coord2: List[float]) -> float:
    """Calculates ground distance in meters between two lat/lng coordinates."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_evacuation_route(
    zone_id: int,
    hazard_zone_ids: Optional[List[int]] = None,
    force_blocked: bool = False,
) -> Dict[str, Any]:
    """
    Computes a verified evacuation path from the origin zone to designated safe refuge.
    
    If intermediate corridors cross an active Critical hazard zone or force_blocked is True,
    returns route_status='UNSAFE_BLOCKED' and emergency shelter-in-place instructions.
    """
    hazard_zone_ids = hazard_zone_ids or []
    corridor = CORRIDORS.get(zone_id)

    if not corridor or force_blocked:
        return {
            "route_status": "UNSAFE_BLOCKED",
            "destination_name": "No Safe Route Available",
            "destination_coords": None,
            "waypoints": [],
            "distance_meters": 0.0,
            "est_evacuation_minutes": 0.0,
            "instructions": (
                "EMERGENCY PROCEDURE: All primary egress corridors are obstructed or unsafe. "
                "Do NOT attempt transit through unmapped smoke/rockfall zones. "
                "Immediately seal hermetic blast doors, activate compressed-air breathing apparatus, "
                "and await mine rescue team extraction."
            ),
        }

    # Verify corridor does not traverse OTHER critical hazard zones
    traversed = corridor["traverses_zones"]
    # We allow the origin zone itself, but if an intermediate path zone is also in hazard, check safety
    hazardous_intermediates = [zid for zid in traversed if zid != zone_id and zid in hazard_zone_ids]
    if hazardous_intermediates:
        return {
            "route_status": "UNSAFE_BLOCKED",
            "destination_name": corridor["destination"]["name"],
            "destination_coords": corridor["destination"]["coordinates"],
            "waypoints": [],
            "distance_meters": 0.0,
            "est_evacuation_minutes": 0.0,
            "instructions": (
                f"INTERMEDIATE CORRIDOR BLOCKED: Evacuation route through Zone {hazardous_intermediates} "
                "is compromised by active hazards. Follow secondary emergency protocol: "
                "Shelter in place, seal airtight barricades, and activate emergency beacon."
            ),
        }

    # Calculate total path distance
    waypoints = corridor["waypoints"]
    total_dist = 0.0
    for i in range(len(waypoints) - 1):
        total_dist += haversine_distance_meters(waypoints[i], waypoints[i + 1])

    # Walking speed assumption: 1.0 m/s in emergency mining conditions
    walk_speed_mps = 1.0
    est_seconds = total_dist / walk_speed_mps
    est_minutes = round(est_seconds / 60.0, 1)

    dest = corridor["destination"]

    return {
        "route_status": "SAFE_CLEAR",
        "destination_name": dest["name"],
        "destination_coords": dest["coordinates"],
        "destination_type": dest["type"],
        "waypoints": waypoints,
        "distance_meters": round(total_dist, 1),
        "est_evacuation_minutes": max(1.0, est_minutes),
        "instructions": (
            f"PROCEED IMMEDIATELY along illuminated primary escapeway to {dest['name']}. "
            f"Distance: {round(total_dist, 0)}m (Approx {max(1.0, est_minutes)} mins). "
            "Report arrival upon reaching safe threshold."
        ),
    }
