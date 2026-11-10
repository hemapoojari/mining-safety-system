import React, { useState } from 'react';
import {
  Mountain,
  CloudRain,
  Activity,
  Move,
  AlertTriangle,
  ShieldCheck,
  TrendingUp,
  Compass,
} from 'lucide-react';
import MineMap from '../components/MineMap';
import StatCard from '../components/StatCard';
import { updateZoneRisk } from '../services/api';

export default function OpenPitView({
  zones = [],
  workers = [],
  activeAlerts = [],
  currentReadings = [],
  onRefresh,
}) {
  const [overrideZoneId, setOverrideZoneId] = useState(null);
  const [selectedTier, setSelectedTier] = useState('High');
  const [isUpdating, setIsUpdating] = useState(false);

  const openPitZones = zones.filter((z) => z.mine_type === 'open_pit');
  const openPitWorkers = workers.filter((w) =>
    openPitZones.some((z) => z.id === w.zone_id)
  );

  // Filter open-pit readings
  const opReadings = currentReadings.filter((r) => r.mine_type === 'open_pit');
  const rainSensor = opReadings.find((r) => r.sensor_type === 'rainfall');
  const vibSensor = opReadings.find((r) => r.sensor_type === 'vibration');
  const slopeSensor = opReadings.find((r) => r.sensor_type === 'slope_displacement');
  const crackSensor = opReadings.find((r) => r.sensor_type === 'crack_expansion');
  const soilSensor = opReadings.find((r) => r.sensor_type === 'soil_moisture');
  const drateSensor = opReadings.find((r) => r.sensor_type === 'displacement_rate');

  const handleOverride = async (zoneCode) => {
    setIsUpdating(true);
    try {
      await updateZoneRisk(zoneCode, {
        risk_tier: selectedTier,
        reason: 'Safety Officer Geotechnical Override',
      });
      setOverrideZoneId(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to override zone risk:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Geotechnical Safety Summary */}
      <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-slate-900 border border-emerald-500/20 rounded-2xl p-5 shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl">
            <Mountain className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <span>Open-Pit Geotechnical & Slope Safety Surveillance</span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full font-semibold uppercase">
                Active Wall Monitoring
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              High-frequency multi-sensor kinematics detecting bench crack dilation, pore-pressure rain saturation,
              and blast vibration exceedance to prevent slope failure and rockfall incidents.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-slate-950/70 border border-slate-800 px-3.5 py-2 rounded-xl text-center">
            <span className="text-slate-400 block text-[10px] uppercase">Active Benches</span>
            <span className="text-base font-bold text-slate-100 font-mono">3 Sectors</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 px-3.5 py-2 rounded-xl text-center">
            <span className="text-slate-400 block text-[10px] uppercase">Field Personnel</span>
            <span className="text-base font-bold text-emerald-400 font-mono">{openPitWorkers.length}</span>
          </div>
        </div>
      </div>

      {/* Geotechnical Primary 6-Sensor Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        {/* Rainfall Gauge */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Precipitation
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {rainSensor ? `${rainSensor.latest_value} ${rainSensor.unit}` : '0.0 mm/h'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 25 mm/h</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Safe Runoff</div>
        </div>

        {/* Seismic Vibration */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Vibration (PPV)
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {vibSensor ? `${vibSensor.latest_value} ${vibSensor.unit}` : '0.0 mm/s'}
          </div>
          <p className="text-[11px] text-slate-400">DGMS: &lt; 15 mm/s</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Seismic Normal</div>
        </div>

        {/* Slope Movement Extensometer */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Displacement
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {slopeSensor ? `${slopeSensor.latest_value} ${slopeSensor.unit}` : '0.0 mm'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 5.0 mm</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Borehole Ext.</div>
        </div>

        {/* Joint Crack Expansion */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Crack Dilation
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {crackSensor ? `${crackSensor.latest_value} ${crackSensor.unit}` : '0.0 mm'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 3.0 mm</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Crackmeter</div>
        </div>

        {/* Soil Moisture */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Soil Moisture
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {soilSensor ? `${soilSensor.latest_value} ${soilSensor.unit}` : '20.0 %'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 60 %</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">TDR Probe</div>
        </div>

        {/* Displacement Rate */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Velocity Rate
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {drateSensor ? `${drateSensor.latest_value} ${drateSensor.unit}` : '0.2 mm/d'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 2.0 mm/d</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">InSAR Radar</div>
        </div>
      </div>

      {/* Map & Open-Pit Zones Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Open-Pit Specific Map */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">
            Surface Extraction Benches & Haul Roads
          </h3>
          <p className="text-xs text-slate-400 mb-3">
            Open-pit spatial polygons with slope displacement sensors and live machinery/driller locations
          </p>
          <MineMap
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            height="420px"
            filterType="open_pit"
          />
        </div>

        {/* Right: Open-Pit Zones Status & Manual Risk Override */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">
              Open-Pit Zone Risk Status
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Geotechnical state and safety officer override controls
            </p>

            <div className="space-y-3">
              {openPitZones.map((zone) => {
                const isCrit = zone.current_risk_tier === 'Critical';
                const isHigh = zone.current_risk_tier === 'High';

                return (
                  <div
                    key={zone.id}
                    className={`border rounded-xl p-3.5 transition bg-slate-950/60 ${
                      isCrit
                        ? 'border-red-500/60 bg-red-950/20'
                        : isHigh
                        ? 'border-orange-500/60 bg-orange-950/20'
                        : 'border-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-xs text-slate-100">{zone.name}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                          isCrit
                            ? 'bg-red-500 text-white animate-pulse'
                            : isHigh
                            ? 'bg-orange-500/20 text-orange-400 border border-orange-500/40'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        }`}
                      >
                        {zone.current_risk_tier}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 mb-2">{zone.description}</p>

                    <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
                      <span className="text-slate-500 text-[11px]">
                        Personnel: <strong className="text-slate-200">{zone.active_worker_count || 0}</strong>
                      </span>

                      {overrideZoneId === zone.zone_code ? (
                        <div className="flex items-center gap-1.5">
                          <select
                            value={selectedTier}
                            onChange={(e) => setSelectedTier(e.target.value)}
                            className="bg-slate-800 text-slate-200 text-xs rounded px-2 py-1 border border-slate-700"
                          >
                            <option value="Safe">Safe</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                            <option value="Critical">Critical</option>
                          </select>
                          <button
                            onClick={() => handleOverride(zone.zone_code)}
                            disabled={isUpdating}
                            className="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-[11px] font-semibold"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setOverrideZoneId(null)}
                            className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-[11px]"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setOverrideZoneId(zone.zone_code)}
                          className="text-[11px] text-slate-400 hover:text-slate-100 hover:underline"
                        >
                          Manual Override
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Rockfall Trajectory Model:</span>
            <span className="text-slate-400 font-mono">XGBoost / Random Forest Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
}
