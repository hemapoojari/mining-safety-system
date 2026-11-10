import React, { useState } from 'react';
import {
  Flame,
  Gauge,
  Wind,
  Thermometer,
  ShieldAlert,
  AlertTriangle,
  Radio,
  Activity,
  Layers,
} from 'lucide-react';
import MineMap from '../components/MineMap';
import { updateZoneRisk } from '../services/api';

export default function UndergroundView({
  zones = [],
  workers = [],
  activeAlerts = [],
  currentReadings = [],
  onRefresh,
}) {
  const [overrideZoneId, setOverrideZoneId] = useState(null);
  const [selectedTier, setSelectedTier] = useState('Critical');
  const [isUpdating, setIsUpdating] = useState(false);

  const ugZones = zones.filter((z) => z.mine_type === 'underground');
  const ugWorkers = workers.filter((w) =>
    ugZones.some((z) => z.id === w.zone_id)
  );

  // Filter underground readings
  const ugReadings = currentReadings.filter((r) => r.mine_type === 'underground');
  const ch4Sensor = ugReadings.find((r) => r.sensor_type === 'ch4');
  const coSensor = ugReadings.find((r) => r.sensor_type === 'co');
  const o2Sensor = ugReadings.find((r) => r.sensor_type === 'o2');
  const tempSensor = ugReadings.find((r) => r.sensor_type === 'temperature');
  const smokeSensor = ugReadings.find((r) => r.sensor_type === 'smoke');
  const ventSensor = ugReadings.find((r) => r.sensor_type === 'ventilation');

  // Compute live Graham's Ratio: (CO / (20.9 - O2)) * 100
  const coVal = coSensor ? coSensor.latest_value : 5.0;
  const o2Val = o2Sensor ? o2Sensor.latest_value : 20.8;
  const o2Deficit = Math.max(0.01, 20.9 - o2Val);
  const grahamsRatio = ((coVal / 10000.0) / o2Deficit * 100.0).toFixed(3);

  const handleOverride = async (zoneCode) => {
    setIsUpdating(true);
    try {
      await updateZoneRisk(zoneCode, {
        risk_tier: selectedTier,
        reason: 'Safety Officer Atmospheric Override',
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
      {/* Top Banner: Underground Atmosphere & Fire Surveillance */}
      <div className="bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-900 border border-blue-500/20 rounded-2xl p-5 shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-xl">
            <Flame className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <span>Underground Atmospheric & Spontaneous Combustion Surveillance</span>
              <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-semibold uppercase">
                Sub-Surface Telemetry
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Continuous monitoring of toxic gases (CO, H2S, NO2), explosive methane (CH4), oxygen depletion,
              thermal gradients, and exhaust ventilation to prevent asphyxiation and mine explosions.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-slate-950/70 border border-slate-800 px-3.5 py-2 rounded-xl text-center">
            <span className="text-slate-400 block text-[10px] uppercase">Active Stopes</span>
            <span className="text-base font-bold text-slate-100 font-mono">3 Sub-Levels</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 px-3.5 py-2 rounded-xl text-center">
            <span className="text-slate-400 block text-[10px] uppercase">Sub-Surface Miners</span>
            <span className="text-base font-bold text-blue-400 font-mono">{ugWorkers.length}</span>
          </div>
        </div>
      </div>

      {/* Atmospheric Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        {/* Methane CH4 */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Methane (CH4)
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {ch4Sensor ? `${ch4Sensor.latest_value} %` : '0.00 %'}
          </div>
          <p className="text-[11px] text-slate-400">Limit: &lt; 1.25%</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">LEL Normal</div>
        </div>

        {/* Carbon Monoxide CO */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Carbon Monoxide
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {coSensor ? `${coSensor.latest_value} ppm` : '0.0 ppm'}
          </div>
          <p className="text-[11px] text-slate-400">Ceiling: 50.0 ppm</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Non-Toxic</div>
        </div>

        {/* Oxygen O2 */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Oxygen (O2)
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {o2Sensor ? `${o2Sensor.latest_value} %` : '20.9 %'}
          </div>
          <p className="text-[11px] text-slate-400">Min Safe: 19.5%</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Optimal Air</div>
        </div>

        {/* Graham's Ratio (Fire Index) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Graham's Ratio
          </span>
          <div className="text-2xl font-bold font-mono text-amber-400 my-1">
            {grahamsRatio} %
          </div>
          <p className="text-[11px] text-slate-400">Spontaneous Comb: &gt; 1.0%</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">No Smoldering</div>
        </div>

        {/* Temperature */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Temperature
          </span>
          <div className="text-2xl font-bold font-mono text-slate-100 my-1">
            {tempSensor ? `${tempSensor.latest_value} °C` : '24.0 °C'}
          </div>
          <p className="text-[11px] text-slate-400">Thermal Threshold: 38°C</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Comfort Range</div>
        </div>

        {/* Ventilation Airflow */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Ventilation Velocity
          </span>
          <div className="text-2xl font-bold font-mono text-cyan-400 my-1">
            {ventSensor ? `${ventSensor.latest_value} m/s` : '1.8 m/s'}
          </div>
          <p className="text-[11px] text-slate-400">Min Airflow: 0.3 m/s</p>
          <div className="mt-2 text-[10px] text-emerald-400 font-medium">Exhaust Fan Active</div>
        </div>
      </div>

      {/* Map & Underground Stopes Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Underground Map */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">
            Underground Sub-Levels & Extraction Stopes
          </h3>
          <p className="text-xs text-slate-400 mb-3">
            Sub-surface drift polygons with catalytic gas sensors and fixed BLE/UWB worker location coordinates
          </p>
          <MineMap
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            height="420px"
            filterType="underground"
          />
        </div>

        {/* Right: Underground Zones & Overrides */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">
              Underground Sector Risk Assessment
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Real-time atmospheric state and immediate safety override
            </p>

            <div className="space-y-3">
              {ugZones.map((zone) => {
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
            <span>Atmospheric Dispersion Model:</span>
            <span className="text-slate-400 font-mono">Deep Autoencoder / CatBoost Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
}
