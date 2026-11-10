import React from 'react';
import {
  Users,
  Grid,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  BellRing,
  Activity,
  ArrowRight,
  CloudRain,
  Flame,
  Wind,
  Gauge,
  Move,
} from 'lucide-react';
import StatCard from '../components/StatCard';
import MineMap from '../components/MineMap';

export default function OverviewView({
  zones = [],
  workers = [],
  activeAlerts = [],
  currentReadings = [],
  setCurrentView,
}) {
  const totalWorkers = workers.length;
  const totalZones = zones.length;
  const safeZones = zones.filter((z) => z.current_risk_tier === 'Safe').length;
  const highRiskZones = zones.filter((z) => z.current_risk_tier === 'High').length;
  const criticalZones = zones.filter((z) => z.current_risk_tier === 'Critical').length;
  const activeAlertCount = activeAlerts.length;

  // Find key sensor values
  const getLatestSensor = (type) => {
    const found = currentReadings.find((r) => r.sensor_type === type);
    return found ? `${found.latest_value} ${found.unit}` : '--';
  };

  return (
    <div className="space-y-6">
      {/* Active Emergency Banner (if any) */}
      {activeAlertCount > 0 && (
        <div className="bg-red-950/80 border border-red-600/70 rounded-2xl p-4 shadow-2xl flex flex-wrap items-center justify-between gap-4 animate-pulse">
          <div className="flex items-center space-x-3.5">
            <div className="bg-red-600 p-2.5 rounded-xl text-white shadow-lg shadow-red-600/50">
              <AlertOctagon className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm md:text-base text-white tracking-wide uppercase">
                  Active Emergency Evacuation Triggered
                </span>
                <span className="bg-red-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase">
                  Level 5 Hazard
                </span>
              </div>
              <p className="text-xs text-red-200 mt-0.5">
                {activeAlerts[0].message} ({activeAlerts[0].affected_workers_count} personnel affected)
              </p>
            </div>
          </div>

          <button
            onClick={() => setCurrentView('alerts')}
            className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition shadow-lg flex items-center gap-1.5"
          >
            <span>Evacuation Command Console</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        <StatCard
          title="Total Personnel"
          value={totalWorkers}
          subtext={`${workers.filter((w) => w.status === 'active').length} on active shift`}
          icon={Users}
          variant="neutral"
        />
        <StatCard
          title="Mining Sectors"
          value={totalZones}
          subtext="3 Open-Pit • 3 Underground"
          icon={Grid}
          variant="low"
        />
        <StatCard
          title="Safe Zones"
          value={safeZones}
          subtext="Nominal operating baselines"
          icon={ShieldCheck}
          variant="safe"
        />
        <StatCard
          title="High-Risk Zones"
          value={highRiskZones}
          subtext="Work paused / Alert standby"
          icon={AlertTriangle}
          variant={highRiskZones > 0 ? 'high' : 'neutral'}
        />
        <StatCard
          title="Critical Zones"
          value={criticalZones}
          subtext="Evacuation zone active"
          icon={AlertOctagon}
          variant={criticalZones > 0 ? 'critical' : 'neutral'}
        />
        <StatCard
          title="Active Alerts"
          value={activeAlertCount}
          subtext={activeAlertCount === 0 ? 'All zones cleared' : 'Response ongoing'}
          icon={BellRing}
          variant={activeAlertCount > 0 ? 'critical' : 'safe'}
        />
      </div>

      {/* Main Center: Digital Twin Map & Telemetry Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Map */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                  Mine Digital Twin (Live Geofence Map)
                </h3>
                <p className="text-xs text-slate-400">
                  Real-time surface bench polygons, underground stopes, and live worker tracking
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-medium text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-lg">
                  Basin: 23.7435° N, 86.4150° E
                </span>
              </div>
            </div>

            <MineMap
              zones={zones}
              workers={workers}
              activeAlerts={activeAlerts}
              height="480px"
              filterType="all"
            />
          </div>
        </div>

        {/* Right: Real-time Multi-hazard Telemetry Cards */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-400" />
                  <span>Key Telemetry Snapshot</span>
                </h3>
                <button
                  onClick={() => setCurrentView('sensors')}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium"
                >
                  View All &rarr;
                </button>
              </div>

              <div className="space-y-3">
                {/* Rainfall */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                      <CloudRain className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Precipitation Rate</p>
                      <p className="text-[10px] text-slate-400">Open-Pit Surface Catchment</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('rainfall')}
                    </span>
                  </div>
                </div>

                {/* Ground Vibration */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                      <Activity className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Peak Vibration (PPV)</p>
                      <p className="text-[10px] text-slate-400">Bench Blast & Seismograph</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('vibration')}
                    </span>
                  </div>
                </div>

                {/* Slope Displacement */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
                      <Move className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Slope Crack Movement</p>
                      <p className="text-[10px] text-slate-400">Borehole Extensometers</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('slope_displacement')}
                    </span>
                  </div>
                </div>

                {/* Methane Gas */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-500/10 text-orange-400 rounded-lg">
                      <Flame className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Methane (CH4)</p>
                      <p className="text-[10px] text-slate-400">Underground Stope Face</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('ch4')}
                    </span>
                  </div>
                </div>

                {/* Carbon Monoxide */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-500/10 text-red-400 rounded-lg">
                      <Gauge className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Carbon Monoxide (CO)</p>
                      <p className="text-[10px] text-slate-400">Toxic Gas Sensor</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('co')}
                    </span>
                  </div>
                </div>

                {/* Ventilation Velocity */}
                <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/10 text-cyan-400 rounded-lg">
                      <Wind className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Airflow Velocity</p>
                      <p className="text-[10px] text-slate-400">Return Ventilation Airway</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {getLatestSensor('ventilation')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions Footer */}
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>Evacuation Gateway:</span>
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Targeted Dispatch Armed
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
