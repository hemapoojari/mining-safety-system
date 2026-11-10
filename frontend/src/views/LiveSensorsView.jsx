import React, { useState } from 'react';
import {
  Activity,
  CloudRain,
  Flame,
  Gauge,
  Move,
  Thermometer,
  Wind,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  Send,
  Zap,
} from 'lucide-react';
import { submitSensorReading } from '../services/api';

const SENSOR_ICONS = {
  rainfall: CloudRain,
  vibration: Activity,
  slope_displacement: Move,
  crack_expansion: Move,
  soil_moisture: CloudRain,
  displacement_rate: Zap,
  ch4: Flame,
  co: Gauge,
  o2: Activity,
  temperature: Thermometer,
  smoke: Flame,
  ventilation: Wind,
};

export default function LiveSensorsView({
  currentReadings = [],
  zones = [],
  onRefresh,
}) {
  const [search, setSearch] = useState('');
  const [sectorFilter, setSectorFilter] = useState('all'); // all, open_pit, underground
  const [typeFilter, setTypeFilter] = useState('all');
  const [injectModalSensor, setInjectModalSensor] = useState(null);
  const [injectValue, setInjectValue] = useState('');
  const [isInjecting, setIsInjecting] = useState(false);

  const filtered = currentReadings.filter((sensor) => {
    const matchesSearch =
      sensor.sensor_code.toLowerCase().includes(search.toLowerCase()) ||
      sensor.name.toLowerCase().includes(search.toLowerCase()) ||
      sensor.zone_name.toLowerCase().includes(search.toLowerCase());

    const matchesSector = sectorFilter === 'all' || sensor.mine_type === sectorFilter;
    const matchesType = typeFilter === 'all' || sensor.sensor_type === typeFilter;

    return matchesSearch && matchesSector && matchesType;
  });

  const handleInjectSubmit = async (e) => {
    e.preventDefault();
    if (!injectModalSensor || !injectValue) return;

    setIsInjecting(true);
    try {
      await submitSensorReading({
        sensor_code: injectModalSensor.sensor_code,
        zone_id: injectModalSensor.zone_id,
        mine_type: injectModalSensor.mine_type,
        sensor_type: injectModalSensor.sensor_type,
        value: parseFloat(injectValue),
        unit: injectModalSensor.unit,
      });
      setInjectModalSensor(null);
      setInjectValue('');
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to submit reading:', err);
    } finally {
      setIsInjecting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search sensor code, instrument name, or zone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2">
          {/* Sector Filter */}
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Sectors</option>
            <option value="open_pit">Open-Pit</option>
            <option value="underground">Underground</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Sensor Types</option>
            <option value="rainfall">Rainfall</option>
            <option value="vibration">Vibration</option>
            <option value="slope_displacement">Slope Displacement</option>
            <option value="ch4">Methane (CH4)</option>
            <option value="co">Carbon Monoxide (CO)</option>
            <option value="o2">Oxygen (O2)</option>
            <option value="temperature">Temperature</option>
            <option value="smoke">Smoke</option>
            <option value="ventilation">Ventilation</option>
          </select>
        </div>
      </div>

      {/* Sensor Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((sensor) => {
          const Icon = SENSOR_ICONS[sensor.sensor_type] || Activity;
          const isUnderground = sensor.mine_type === 'underground';

          return (
            <div
              key={sensor.sensor_code}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl hover:border-slate-700 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2.5">
                    <div
                      className={`p-2 rounded-xl ${
                        isUnderground
                          ? 'bg-blue-500/10 text-blue-400'
                          : 'bg-emerald-500/10 text-emerald-400'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="font-mono text-xs font-bold text-slate-100 block">
                        {sensor.sensor_code}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wide">
                        {sensor.sensor_type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-medium capitalize">
                    {sensor.mine_type.replace('_', ' ')}
                  </span>
                </div>

                <p className="text-xs font-semibold text-slate-200 mt-2 line-clamp-1">
                  {sensor.name}
                </p>
                <p className="text-[11px] text-slate-400">{sensor.zone_name}</p>

                {/* Big Live Value Display */}
                <div className="my-4 p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl flex items-baseline justify-between">
                  <div>
                    <span className="text-xs text-slate-500 block">Live Reading</span>
                    <span className="text-2xl font-bold font-mono text-slate-100">
                      {sensor.latest_value}
                    </span>
                  </div>
                  <span className="text-xs font-semibold text-slate-400 font-mono">
                    {sensor.unit}
                  </span>
                </div>
              </div>

              {/* Action Bar */}
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-emerald-400 flex items-center gap-1 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Telemetry Online
                </span>

                <button
                  onClick={() => {
                    setInjectModalSensor(sensor);
                    setInjectValue(sensor.latest_value);
                  }}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-[11px] font-medium transition flex items-center gap-1"
                  title="Inject test sensor reading to verify threshold engine"
                >
                  <Zap className="w-3 h-3 text-amber-400" />
                  <span>Test Input</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Manual Injection Modal */}
      {injectModalSensor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-1 flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-400" />
              <span>Submit Sensor Value Test</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Inject a custom reading for <strong>{injectModalSensor.sensor_code}</strong> ({injectModalSensor.name}).
              High values will trigger automated risk escalation and targeted emergency alerts.
            </p>

            <form onSubmit={handleInjectSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Sensor Reading ({injectModalSensor.unit})
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={injectValue}
                  onChange={(e) => setInjectValue(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setInjectModalSensor(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isInjecting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Submit & Trigger Risk Check</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
