import React, { useState } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { ShieldAlert, AlertTriangle, User, HardHat, Mountain, Flame, Shield, Flag } from 'lucide-react';

// Fix default Leaflet icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Color mapping for 5 Risk Tiers
const RISK_COLORS = {
  Safe: { stroke: '#22c55e', fill: '#22c55e', fillOpacity: 0.25 },
  Low: { stroke: '#0ea5e9', fill: '#0ea5e9', fillOpacity: 0.25 },
  Medium: { stroke: '#eab308', fill: '#eab308', fillOpacity: 0.35 },
  High: { stroke: '#f97316', fill: '#f97316', fillOpacity: 0.45 },
  Critical: { stroke: '#ef4444', fill: '#ef4444', fillOpacity: 0.6 },
};

// Create custom Worker Marker Icon
const createWorkerIcon = (status) => {
  const isEvac = status === 'evacuating';
  const isTrapped = status === 'trapped';
  const isSafe = status === 'safe';

  let bg = '#0284c7'; // active default
  if (isEvac) bg = '#ea580c';
  if (isTrapped) bg = '#dc2626';
  if (isSafe) bg = '#16a34a';

  return L.divIcon({
    className: 'custom-worker-marker',
    html: `
      <div style="
        background-color: ${bg};
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
        box-shadow: 0 0 8px rgba(0,0,0,0.5);
        color: white;
        font-size: 11px;
        font-weight: bold;
        ${isEvac || isTrapped ? 'animation: pulse 1.5s infinite;' : ''}
      ">
        👷
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

// Create custom Safe Refuge Point Icon
const createRefugeIcon = (type) => {
  const isChamber = type === 'hermetic_refuge_chamber';
  const isPortal = type === 'mine_portal';
  const bg = isChamber ? '#0891b2' : isPortal ? '#2563eb' : '#15803d';
  const iconEmoji = isChamber ? '🛡️' : isPortal ? '🚪' : '🏁';

  return L.divIcon({
    className: 'custom-refuge-marker',
    html: `
      <div style="
        background-color: ${bg};
        width: 28px;
        height: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
        box-shadow: 0 0 10px rgba(0,0,0,0.6);
        color: white;
        font-size: 14px;
      ">
        ${iconEmoji}
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

const SAFE_REFUGES = [
  {
    id: 'surface_muster',
    name: 'North Pit Surface Muster Station',
    position: [23.7480, 86.4160],
    type: 'surface_muster',
    capacity: '100 Personnel',
    description: 'Designated open-air muster ground outside rockfall runout limit.',
  },
  {
    id: 'refuge_chamber',
    name: 'Underground Fresh-Air Refuge Chamber #1',
    position: [23.7428, 86.4122],
    type: 'hermetic_refuge_chamber',
    capacity: '30 Personnel (48h O2)',
    description: 'Positive-pressure hermetic blast shelter with independent life support.',
  },
  {
    id: 'main_portal',
    name: 'Main Incline Drift Portal (Surface Adit)',
    position: [23.7445, 86.4145],
    type: 'mine_portal',
    capacity: '200 Personnel',
    description: 'Fresh-air intake drift portal exiting directly to surface.',
  },
];

export default function MineMap({
  zones = [],
  workers = [],
  activeAlerts = [],
  height = '460px',
  filterType = 'all', // 'all', 'open_pit', 'underground'
}) {
  const defaultCenter = [23.7435, 86.4150]; // Mining Basin Center

  const filteredZones = zones.filter((z) => {
    if (filterType === 'all') return true;
    return z.mine_type === filterType;
  });

  // Extract active evacuation routes from active emergency alerts
  const activeRoutes = activeAlerts
    .map((alert) => {
      if (!alert.route_details) return null;
      try {
        const details = typeof alert.route_details === 'string' ? JSON.parse(alert.route_details) : alert.route_details;
        return {
          alertId: alert.id,
          alertCode: alert.alert_code,
          zoneId: alert.zone_id,
          zoneName: alert.zone_name,
          ...details,
        };
      } catch (e) {
        return null;
      }
    })
    .filter(Boolean);

  const blockedRoutes = activeRoutes.filter((r) => r.route_status === 'UNSAFE_BLOCKED');

  return (
    <div style={{ height }} className="w-full relative rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <MapContainer
        center={defaultCenter}
        zoom={16}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Mining Zone Geofence Polygons */}
        {filteredZones.map((zone) => {
          let coordinates = [];
          try {
            coordinates = JSON.parse(zone.boundary_geo);
          } catch (e) {
            coordinates = [];
          }

          if (!coordinates || coordinates.length < 3) return null;

          const colors = RISK_COLORS[zone.current_risk_tier] || RISK_COLORS.Safe;
          const isCritical = zone.current_risk_tier === 'Critical';

          return (
            <Polygon
              key={zone.id}
              positions={coordinates}
              pathOptions={{
                color: colors.stroke,
                weight: isCritical ? 4 : 2,
                fillColor: colors.fill,
                fillOpacity: colors.fillOpacity,
                dashArray: zone.mine_type === 'underground' ? '6, 6' : undefined,
              }}
            >
              <Popup>
                <div className="text-slate-900 font-sans min-w-[200px]">
                  <div className="flex items-center justify-between border-b pb-1.5 mb-1.5">
                    <span className="font-bold text-xs uppercase tracking-wide text-slate-800">
                      {zone.zone_code}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        zone.current_risk_tier === 'Critical'
                          ? 'bg-red-100 text-red-700'
                          : zone.current_risk_tier === 'High'
                          ? 'bg-orange-100 text-orange-700'
                          : zone.current_risk_tier === 'Medium'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {zone.current_risk_tier}
                    </span>
                  </div>

                  <p className="font-semibold text-sm text-slate-900 mb-1">{zone.name}</p>
                  <p className="text-[11px] text-slate-600 mb-2">{zone.description}</p>

                  <div className="bg-slate-100 rounded p-2 text-[11px] space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Sector:</span>
                      <span className="font-semibold text-slate-800 capitalize">
                        {zone.mine_type.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Personnel in Zone:</span>
                      <span className="font-semibold text-slate-800">
                        {zone.active_worker_count || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Polygon>
          );
        })}

        {/* Active Evacuation Route Polylines */}
        {activeRoutes.map((route, idx) => {
          if (!route.waypoints || route.waypoints.length < 2) return null;
          const isBlocked = route.route_status === 'UNSAFE_BLOCKED';

          return (
            <Polyline
              key={`route-${route.alertId || idx}`}
              positions={route.waypoints}
              pathOptions={{
                color: isBlocked ? '#ef4444' : '#f59e0b',
                weight: 4,
                dashArray: '8, 8',
                opacity: 0.9,
              }}
            >
              <Popup>
                <div className="text-slate-900 font-sans text-xs min-w-[220px]">
                  <div className="flex items-center justify-between border-b pb-1 mb-1">
                    <span className="font-bold text-amber-700 uppercase">
                      Evacuation Escapeway
                    </span>
                    <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold">
                      {route.alertCode}
                    </span>
                  </div>
                  <p className="font-bold text-sm text-slate-900 mb-0.5">
                    Destination: {route.destination_name}
                  </p>
                  <p className="text-slate-600 mb-1">
                    Distance: {route.distance_meters}m (~{route.est_evacuation_minutes} min)
                  </p>
                  <div className="bg-slate-100 p-1.5 rounded text-[11px] text-slate-700">
                    {route.instructions}
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        {/* Safe Refuge Stations */}
        {SAFE_REFUGES.map((refuge) => (
          <Marker
            key={refuge.id}
            position={refuge.position}
            icon={createRefugeIcon(refuge.type)}
          >
            <Popup>
              <div className="text-slate-900 font-sans min-w-[210px]">
                <div className="flex items-center justify-between border-b pb-1 mb-1">
                  <span className="font-bold text-xs text-emerald-700 uppercase">
                    Safe Refuge Point
                  </span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                    Capacity: {refuge.capacity}
                  </span>
                </div>
                <p className="font-bold text-sm text-slate-900 mb-1">{refuge.name}</p>
                <p className="text-xs text-slate-600">{refuge.description}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Worker Markers */}
        {workers.map((worker) => {
          if (!worker.current_lat || !worker.current_lng) return null;

          return (
            <Marker
              key={worker.id}
              position={[worker.current_lat, worker.current_lng]}
              icon={createWorkerIcon(worker.status)}
            >
              <Popup>
                <div className="text-slate-900 font-sans min-w-[180px]">
                  <div className="flex items-center justify-between border-b pb-1 mb-1">
                    <span className="font-bold text-xs text-slate-800">{worker.worker_code}</span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${
                        worker.status === 'evacuating'
                          ? 'bg-orange-100 text-orange-700'
                          : worker.status === 'trapped'
                          ? 'bg-red-100 text-red-700'
                          : worker.status === 'safe'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {worker.status}
                    </span>
                  </div>
                  <p className="font-bold text-sm text-slate-900">{worker.full_name}</p>
                  <p className="text-xs text-slate-600 mb-1.5">{worker.role}</p>

                  <div className="text-[11px] text-slate-500 space-y-0.5">
                    <div>
                      <span className="font-semibold text-slate-700">Location: </span>
                      {worker.elevation_or_level || 'Ground'}
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">Zone: </span>
                      {worker.zone_name || 'Unassigned'}
                    </div>
                    <div className="text-[10px] text-slate-400 italic mt-1">
                      Simulated Demonstration Coordinates
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Blocked Route Alert Floating Banner (if any) */}
      {blockedRoutes.length > 0 && (
        <div className="absolute top-3 left-3 right-3 z-[1000] bg-red-950/90 border border-red-500/80 rounded-xl p-2.5 text-xs text-red-200 shadow-2xl flex items-center justify-between backdrop-blur animate-pulse">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>
              <strong>EMERGENCY CAUTION:</strong> Direct egress route obstructed for {blockedRoutes.map(r => r.zoneName).join(', ')}. Follow shelter-in-place procedure behind hermetic seals.
            </span>
          </div>
        </div>
      )}

      {/* Map Legend Floating Overlay */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-slate-950/85 backdrop-blur border border-slate-800/90 rounded-xl p-3 text-[11px] text-slate-300 shadow-xl pointer-events-auto">
        <span className="font-semibold text-slate-100 block mb-2 text-[10px] uppercase tracking-wider">
          Risk & Evacuation Legend
        </span>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500 border border-emerald-400" />
            <span>Safe (L1)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-sky-500 border border-sky-400" />
            <span>Low (L2)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-500 border border-amber-400" />
            <span>Medium (L3)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-orange-500 border border-orange-400" />
            <span>High (L4)</span>
          </div>
          <div className="flex items-center gap-1.5 col-span-2">
            <span className="w-3 h-3 rounded bg-red-600 border border-red-400 animate-pulse" />
            <span className="font-bold text-red-400">Critical (L5 Evacuate)</span>
          </div>
          <div className="flex items-center gap-1.5 col-span-2 pt-1 border-t border-slate-800">
            <span className="w-5 h-0.5 border-t-2 border-dashed border-amber-400" />
            <span className="text-amber-300">Evacuation Escapeway</span>
          </div>
          <div className="flex items-center gap-1.5 col-span-2">
            <span>🛡️ / 🏁</span>
            <span className="text-cyan-300">Safe Refuge Station</span>
          </div>
        </div>
      </div>
    </div>
  );
}
