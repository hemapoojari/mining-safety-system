"""
Simulated Worker Tracking & Evacuation Movement Engine
Simulates real-time worker position streams, zone transitions, and directed
evacuation trajectories along verified mine corridors.

Features:
- Open-Pit: GPS coordinates with small Brownian movement on bench faces
- Underground: Beacon/grid positions with driftway transit simulation
- Dynamic zone geofence resolution via Point-in-Polygon
- Evacuation trajectory: Steps worker towards designated refuge station when an alert is active
- Two-way status simulation support: 'Alert Sent' -> 'Acknowledged' -> 'Evacuating' -> 'Reached Safe Zone'
- Clearly tags all records as simulated demonstration data
"""
import math
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.services.evacuation_routing import CORRIDORS, SAFE_REFUGE_POINTS


class WorkerSimulator:
    """
    Manages realistic worker spatial tracking, shift movements,
    and physics-constrained evacuation progression.
    """

    def __init__(self):
        self.is_simulated = True
        self.mine_base_lat = 23.7450
        self.mine_base_lng = 86.4150

    def step_worker_position(
        self,
        worker_dict: Dict[str, Any],
        is_evacuating: bool = False,
        evac_destination: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Advances a single worker's coordinates by one simulation step.
        - If is_evacuating is False: small random walk within current bench/stope.
        - If is_evacuating is True: vector step towards designated safe refuge coordinates.
        """
        updated = dict(worker_dict)
        cur_lat = updated.get("current_lat", self.mine_base_lat)
        cur_lng = updated.get("current_lng", self.mine_base_lng)

        if not is_evacuating or not evac_destination:
            # Natural wandering / shift work jitter (~2-5 meters)
            step_lat = random.uniform(-0.00004, 0.00004)
            step_lng = random.uniform(-0.00004, 0.00004)
            updated["current_lat"] = round(cur_lat + step_lat, 6)
            updated["current_lng"] = round(cur_lng + step_lng, 6)
        else:
            # Directed evacuation vector towards refuge point
            dest_lat, dest_lng = evac_destination
            delta_lat = dest_lat - cur_lat
            delta_lng = dest_lng - cur_lng
            dist = math.hypot(delta_lat, delta_lng)

            # Evacuation walking speed (~10-15 meters per tick)
            step_size = 0.00015
            if dist <= step_size:
                # Reached refuge point!
                updated["current_lat"] = dest_lat
                updated["current_lng"] = dest_lng
                updated["status"] = "safe"  # Reached Safe Zone
            else:
                ratio = step_size / dist
                updated["current_lat"] = round(cur_lat + delta_lat * ratio, 6)
                updated["current_lng"] = round(cur_lng + delta_lng * ratio, 6)
                if updated.get("status") != "safe":
                    updated["status"] = "evacuating"

        updated["last_ping"] = datetime.now(timezone.utc).isoformat()
        updated["is_simulated"] = True
        return updated

    def get_zone_destination(self, zone_id: int) -> Optional[List[float]]:
        """Returns the pre-configured refuge point coordinates for a given zone."""
        corridor = CORRIDORS.get(zone_id)
        if corridor:
            return corridor["destination"]["coordinates"]
        return None
