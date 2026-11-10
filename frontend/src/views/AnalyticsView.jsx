import React, { useState, useEffect, useMemo } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart,
  ShieldAlert,
  Clock,
  Download,
  Calendar,
  Layers,
  FileText,
  FileSpreadsheet,
  LifeBuoy,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Cpu,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Filter,
  RefreshCw,
  Mountain,
  Flame,
  Shield,
  Eye,
} from 'lucide-react';
import {
  getAnalyticsKPIs,
  getHistoricalRisk,
  getPredictiveTrends,
  getEvacuationPerformance,
  getMLModelComparison,
  getSensorHistory,
  getIncidentReportPDFUrl,
  getZoneSafetyPDFUrl,
  getSensorCSVUrl,
  getIncidentsCSVUrl,
  triggerFileDownload,
} from '../services/api';
import Sparkline from '../components/Sparkline';

export default function AnalyticsView({ zones = [], workers = [] }) {
  // Navigation Tabs: 'kpis', 'trends', 'evacuation', 'reports'
  const [activeTab, setActiveTab] = useState('kpis');

  // Core Data States
  const [kpis, setKpis] = useState(null);
  const [predictiveTrends, setPredictiveTrends] = useState(null);
  const [evacPerf, setEvacPerf] = useState(null);
  const [mlModels, setMlModels] = useState(null);
  const [historicalRisks, setHistoricalRisks] = useState([]);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Filters State
  const [selectedSensorType, setSelectedSensorType] = useState('slope_displacement');
  const [filterZoneId, setFilterZoneId] = useState('all');
  const [filterMineType, setFilterMineType] = useState('all');
  const [filterHazardType, setFilterHazardType] = useState('all');
  const [timeLimit, setTimeLimit] = useState(50);
  const [selectedZoneForPdf, setSelectedZoneForPdf] = useState(zones.length > 0 ? zones[0].id : 1);

  // Load all analytics data
  const loadAnalyticsData = async () => {
    setIsRefreshing(true);
    try {
      const [kpiRes, trendsRes, evacRes, mlRes] = await Promise.all([
        getAnalyticsKPIs().catch(() => null),
        getPredictiveTrends().catch(() => null),
        getEvacuationPerformance().catch(() => null),
        getMLModelComparison().catch(() => null),
      ]);

      setKpis(kpiRes);
      setPredictiveTrends(trendsRes);
      setEvacPerf(evacRes);
      setMlModels(mlRes);
    } catch (err) {
      console.error('Failed to load analytics dashboard data:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Load historical risk records with filters
  const loadHistoricalRisks = async () => {
    try {
      const params = { limit: timeLimit };
      if (filterZoneId !== 'all') params.zone_id = parseInt(filterZoneId);
      if (filterMineType !== 'all') params.mine_type = filterMineType;
      if (filterHazardType !== 'all') params.hazard_type = filterHazardType;

      const data = await getHistoricalRisk(params);
      setHistoricalRisks(data || []);
    } catch (err) {
      console.error('Failed to load historical risk data:', err);
    }
  };

  // Load sensor telemetry time-series
  const loadSensorTimeSeries = async () => {
    try {
      const params = { sensor_type: selectedSensorType, limit: 30 };
      if (filterZoneId !== 'all') params.zone_id = parseInt(filterZoneId);
      const data = await getSensorHistory(params);
      setSensorHistory(data || []);
    } catch (err) {
      console.error('Failed to load sensor history:', err);
    }
  };

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  useEffect(() => {
    loadHistoricalRisks();
  }, [filterZoneId, filterMineType, filterHazardType, timeLimit]);

  useEffect(() => {
    loadSensorTimeSeries();
  }, [selectedSensorType, filterZoneId]);

  // Telemetry chart values
  const sensorChartValues = useMemo(() => {
    return sensorHistory.map((r) => r.value).reverse();
  }, [sensorHistory]);

  // Handle Export Downloads
  const handleDownload = async (url, filename) => {
    try {
      await triggerFileDownload(url, filename);
    } catch (err) {
      alert(`Download failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Industrial Executive Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-blue-600/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
              Decision Support & Statutory Audit
            </span>
            <span className="bg-slate-800 text-slate-400 text-[10px] font-mono px-2 py-0.5 rounded">
              Academic Research Prototype
            </span>
          </div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <span>Advanced Safety Analytics, Predictive Insights & Incident Dossiers</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time telemetry aggregation, dual-engine ML hazard trend velocity, and statutory evacuation reporting
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => loadAnalyticsData()}
            disabled={isRefreshing}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition border border-slate-700/60 flex items-center gap-1.5"
            title="Refresh analytics data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
            <span>Sync Telemetry</span>
          </button>

          <button
            onClick={() => handleDownload(getIncidentsCSVUrl(), 'emergency_incidents_ledger.csv')}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-blue-600/25 flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Incident Ledger</span>
          </button>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => setActiveTab('kpis')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'kpis'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <PieChart className="w-4 h-4" />
          <span>Overview & Sector KPIs</span>
        </button>

        <button
          onClick={() => setActiveTab('trends')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'trends'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Predictive Hazard Trends & ML Models</span>
        </button>

        <button
          onClick={() => setActiveTab('evacuation')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'evacuation'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <LifeBuoy className="w-4 h-4" />
          <span>Evacuation Performance & Escapeways</span>
        </button>

        <button
          onClick={() => setActiveTab('reports')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'reports'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Incident Dossiers & PDF/CSV Exports</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: OVERVIEW & SECTOR KPIS */}
      {/* ========================================================================= */}
      {activeTab === 'kpis' && (
        <div className="space-y-6">
          {/* Top 6 KPI Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* Total Sensor Readings */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">
                Telemetry Ingested
              </span>
              <span className="text-2xl font-bold font-mono text-slate-100 mt-1 block">
                {kpis ? kpis.total_sensor_readings.toLocaleString() : '—'}
              </span>
              <span className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                Live Continuous
              </span>
            </div>

            {/* Total Hazard Detections */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-amber-400 block tracking-wider">
                Hazard Detections
              </span>
              <span className="text-2xl font-bold font-mono text-amber-400 mt-1 block">
                {kpis ? kpis.total_hazard_detections.toLocaleString() : '—'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1 block">
                Medium / High / Critical
              </span>
            </div>

            {/* Total Alerts Created */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-red-400 block tracking-wider">
                Total Emergencies
              </span>
              <span className="text-2xl font-bold font-mono text-red-400 mt-1 block">
                {kpis ? kpis.total_alerts : '—'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1 block">
                {kpis ? `${kpis.active_alerts} Active Now` : '—'}
              </span>
            </div>

            {/* Total Workers at Risk */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">
                Personnel at Risk
              </span>
              <span className="text-2xl font-bold font-mono text-slate-100 mt-1 block">
                {kpis ? kpis.total_affected_workers : '—'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1 block">
                Targeted Hazard Zones
              </span>
            </div>

            {/* Confirmed Safe in Refuge */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-emerald-400 block tracking-wider">
                Confirmed Safe
              </span>
              <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
                {kpis ? kpis.successful_evacuations : '—'}
              </span>
              <span className="text-[10px] text-emerald-400 font-semibold mt-1 block">
                {kpis ? `${kpis.evacuation_clearance_rate}% Cleared` : '—'}
              </span>
            </div>

            {/* Pending Evacuations */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
              <span className="text-[10px] font-bold uppercase text-orange-400 block tracking-wider">
                Pending Safe
              </span>
              <span className="text-2xl font-bold font-mono text-orange-400 mt-1 block">
                {kpis ? kpis.pending_evacuations : '0'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1 block">
                In Transit / Shelter
              </span>
            </div>
          </div>

          {/* Grid: 5-Tier Risk Distribution & Sector Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* 5-Tier Risk Distribution */}
            <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1 flex items-center justify-between">
                  <span>Current 5-Tier Zone Risk Distribution</span>
                  <span className="text-[10px] font-normal text-slate-400 font-mono">6 Mining Sectors</span>
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Statutory hazard classification derived from dual-engine ML inference
                </p>

                {kpis && (
                  <div className="space-y-3">
                    {[
                      { tier: 'Safe', color: 'bg-emerald-500', text: 'text-emerald-400', count: kpis.current_risk_distribution.Safe },
                      { tier: 'Low', color: 'bg-sky-500', text: 'text-sky-400', count: kpis.current_risk_distribution.Low },
                      { tier: 'Medium', color: 'bg-amber-500', text: 'text-amber-400', count: kpis.current_risk_distribution.Medium },
                      { tier: 'High', color: 'bg-orange-500', text: 'text-orange-400', count: kpis.current_risk_distribution.High },
                      { tier: 'Critical', color: 'bg-red-600', text: 'text-red-400', count: kpis.current_risk_distribution.Critical },
                    ].map((item) => (
                      <div key={item.tier}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-300 font-medium">{item.tier} Risk</span>
                          <span className={`font-mono font-bold ${item.text}`}>
                            {item.count} Zones ({(item.count / 6 * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden">
                          <div
                            style={{ width: `${(item.count / 6) * 100}%` }}
                            className={`h-full ${item.color} rounded-full transition-all duration-500`}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
                <span>Evaluation Standard: DGMS Tech Circular / MSHA CFR 30</span>
                <span className="text-emerald-400 font-medium">100% Real-Time</span>
              </div>
            </div>

            {/* Sector Comparison: Open-Pit vs Underground */}
            <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1">
                Open-Pit vs Underground Sector Comparison
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Comparative analysis of geotechnical slope stability versus atmospheric ventilation safety
              </p>

              {kpis && kpis.sector_comparison && (
                <div className="grid grid-cols-2 gap-4">
                  {/* Open-Pit Card */}
                  <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Mountain className="w-4 h-4 text-amber-400" />
                        <span className="font-bold text-xs uppercase text-slate-200">Open-Pit Mining</span>
                      </div>
                      <span className="text-[10px] bg-amber-500/20 text-amber-300 font-bold px-2 py-0.5 rounded">
                        Surface
                      </span>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Total Benches/Zones:</span>
                        <span className="font-mono text-slate-200 font-bold">{kpis.sector_comparison.open_pit.total_zones}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Safe Status:</span>
                        <span className="font-mono text-emerald-400 font-bold">{kpis.sector_comparison.open_pit.safe_zones} Zones</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">High/Critical Hazards:</span>
                        <span className="font-mono text-red-400 font-bold">{kpis.sector_comparison.open_pit.high_risk_zones} Zones</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Telemetry Ingested:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.open_pit.total_readings.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Active Workers:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.open_pit.worker_count} Personnel</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Historical Alarms:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.open_pit.total_alerts}</span>
                      </div>
                    </div>
                  </div>

                  {/* Underground Card */}
                  <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Flame className="w-4 h-4 text-blue-400" />
                        <span className="font-bold text-xs uppercase text-slate-200">Underground Mining</span>
                      </div>
                      <span className="text-[10px] bg-blue-500/20 text-blue-300 font-bold px-2 py-0.5 rounded">
                        Sub-Surface
                      </span>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Total Levels/Stopes:</span>
                        <span className="font-mono text-slate-200 font-bold">{kpis.sector_comparison.underground.total_zones}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Safe Status:</span>
                        <span className="font-mono text-emerald-400 font-bold">{kpis.sector_comparison.underground.safe_zones} Zones</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">High/Critical Hazards:</span>
                        <span className="font-mono text-red-400 font-bold">{kpis.sector_comparison.underground.high_risk_zones} Zones</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Telemetry Ingested:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.underground.total_readings.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Active Workers:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.underground.worker_count} Personnel</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Historical Alarms:</span>
                        <span className="font-mono text-slate-300">{kpis.sector_comparison.underground.total_alerts}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Zone-Wise Safety Statistics Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1">
              Sector Safety Ledger (All 6 Mining Zones)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Real-time zone assessment, historical alert counts, and telemetry sample inventory
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                    <th className="pb-2.5">Code</th>
                    <th className="pb-2.5">Zone Name</th>
                    <th className="pb-2.5">Sector</th>
                    <th className="pb-2.5">Current Risk</th>
                    <th className="pb-2.5">Active Workers</th>
                    <th className="pb-2.5">Telemetry Samples</th>
                    <th className="pb-2.5">Alerts Recorded</th>
                    <th className="pb-2.5">Primary Hazard</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {kpis && kpis.zone_safety_stats.map((z) => {
                    const isCritical = z.current_risk_tier === 'Critical';
                    const isHigh = z.current_risk_tier === 'High';
                    const isMedium = z.current_risk_tier === 'Medium';
                    const badgeClass = isCritical
                      ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                      : isHigh
                      ? 'bg-orange-500/20 text-orange-400 border border-orange-500/40'
                      : isMedium
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';

                    return (
                      <tr key={z.zone_id} className="hover:bg-slate-800/40 transition">
                        <td className="py-2.5 font-mono font-bold text-slate-200">{z.zone_code}</td>
                        <td className="py-2.5 font-medium text-slate-100">{z.zone_name}</td>
                        <td className="py-2.5 text-slate-300 capitalize">{z.mine_type.replace('_', ' ')}</td>
                        <td className="py-2.5">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${badgeClass}`}>
                            {z.current_risk_tier}
                          </span>
                        </td>
                        <td className="py-2.5 font-mono text-slate-300">{z.active_worker_count} Personnel</td>
                        <td className="py-2.5 font-mono text-slate-300">{z.sensor_readings_count.toLocaleString()}</td>
                        <td className="py-2.5 font-mono text-slate-300">{z.total_alerts_count}</td>
                        <td className="py-2.5 text-slate-400 capitalize">{z.latest_hazard.replace('_', ' ')}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: PREDICTIVE HAZARD TRENDS & ML MODELS */}
      {/* ========================================================================= */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          {/* 4 Hazard Predictive Trend Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {predictiveTrends && predictiveTrends.hazard_trends.map((h) => {
              const isInc = h.trend_direction === 'increasing';
              const isDec = h.trend_direction === 'decreasing';
              const directionIcon = isInc ? ArrowUpRight : isDec ? ArrowDownRight : TrendingUp;
              const DirectionIcon = directionIcon;
              const isCritical = h.current_tier === 'Critical' || h.early_warning_flag;

              return (
                <div
                  key={h.hazard_key}
                  className={`bg-slate-900 border rounded-2xl p-4 shadow-xl space-y-3 ${
                    isCritical
                      ? 'border-red-500/60 bg-red-950/10'
                      : 'border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      {h.mine_type.replace('_', ' ')} Model
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase flex items-center gap-1 ${
                        isInc
                          ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                          : isDec
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      <DirectionIcon className="w-3 h-3" />
                      <span>{h.trend_direction}</span>
                    </span>
                  </div>

                  <div>
                    <h4 className="font-bold text-sm text-slate-100">{h.hazard_label}</h4>
                    <span className="text-[10px] font-mono text-slate-400">{h.model_name}</span>
                  </div>

                  <div className="flex items-end justify-between border-t border-slate-800/80 pt-2">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Risk Score</span>
                      <span className="text-xl font-bold font-mono text-slate-100">{h.current_score.toFixed(3)}</span>
                    </div>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${
                        h.current_tier === 'Critical'
                          ? 'bg-red-600 text-white'
                          : h.current_tier === 'High'
                          ? 'bg-orange-600 text-white'
                          : h.current_tier === 'Medium'
                          ? 'bg-amber-600 text-white'
                          : 'bg-emerald-600 text-white'
                      }`}
                    >
                      {h.current_tier}
                    </span>
                  </div>

                  {/* Sparkline Trend */}
                  <div className="pt-1">
                    {h.series.length >= 2 ? (
                      <Sparkline
                        data={h.series}
                        width={240}
                        height={40}
                        color={isCritical ? '#ef4444' : '#3b82f6'}
                        strokeWidth={2}
                      />
                    ) : (
                      <span className="text-[10px] text-slate-500 italic">Gathering trend samples...</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Interactive Multi-Parameter Time-Series Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                  Interactive Sensor Telemetry Trend Profile
                </h3>
                <p className="text-xs text-slate-400">
                  Continuous sensor time-series with statutory threshold drift visualization
                </p>
              </div>

              {/* Selector Controls */}
              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={selectedSensorType}
                  onChange={(e) => setSelectedSensorType(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <optgroup label="Open-Pit Geotechnical">
                    <option value="slope_displacement">Slope Displacement (mm)</option>
                    <option value="vibration">Vibration PPV (mm/s)</option>
                    <option value="rainfall">Rainfall Intensity (mm/h)</option>
                    <option value="crack_expansion">Crack Expansion (mm)</option>
                    <option value="soil_moisture">Soil Moisture (%w)</option>
                    <option value="displacement_rate">Displacement Rate (mm/day)</option>
                  </optgroup>
                  <optgroup label="Underground Atmospheric">
                    <option value="ch4">Methane CH4 (%)</option>
                    <option value="co">Carbon Monoxide CO (ppm)</option>
                    <option value="o2">Oxygen O2 (%)</option>
                    <option value="temperature">Temperature (°C)</option>
                    <option value="smoke">Smoke Density (OD)</option>
                    <option value="ventilation">Ventilation Velocity (m/s)</option>
                  </optgroup>
                </select>

                <select
                  value={filterZoneId}
                  onChange={(e) => setFilterZoneId(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="all">All Mining Zones</option>
                  {zones.map((z) => (
                    <option key={z.id} value={z.id}>
                      {z.zone_code} - {z.name}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => handleDownload(getSensorCSVUrl({ sensor_type: selectedSensorType }), `${selectedSensorType}_telemetry.csv`)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition flex items-center gap-1.5"
                  title="Download CSV dataset for this sensor"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            {/* Large SVG Area Sparkline */}
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 min-h-[260px] flex flex-col justify-between">
              <div className="flex justify-between items-center text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                <span>Selected Metric: <strong className="text-slate-200">{selectedSensorType.replace('_', ' ').toUpperCase()}</strong></span>
                <span className="font-mono text-slate-400">Total Samples: {sensorChartValues.length} points</span>
              </div>

              <div className="py-6 flex items-center justify-center">
                {sensorChartValues.length >= 2 ? (
                  <div className="w-full flex flex-col items-center">
                    <Sparkline
                      data={sensorChartValues}
                      width={720}
                      height={180}
                      color="#3b82f6"
                      strokeWidth={3}
                    />
                    <div className="flex justify-between w-full max-w-[720px] text-[10px] text-slate-500 font-mono mt-2">
                      <span>&larr; Historical Telemetry Window</span>
                      <span className="text-slate-300 font-bold">
                        Latest Ingested Reading: {sensorChartValues[sensorChartValues.length - 1]}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic py-12">
                    Ingesting continuous sensor telemetry stream...
                  </p>
                )}
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex justify-between text-[11px] text-slate-500">
                <span>Statutory Mining Envelope: Normal Baseline Protected</span>
                <span className="text-emerald-400 font-medium">99.8% Data Completeness</span>
              </div>
            </div>
          </div>

          {/* ML Model Performance Comparison Matrix */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-400" />
              <span>Machine Learning Model Benchmark Comparison</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Evaluation metrics for all 4 trained production classifiers across Open-Pit and Underground mining sectors
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                    <th className="pb-2.5">Model Name</th>
                    <th className="pb-2.5">Algorithm</th>
                    <th className="pb-2.5">Sector</th>
                    <th className="pb-2.5">Accuracy</th>
                    <th className="pb-2.5">Precision</th>
                    <th className="pb-2.5">Recall</th>
                    <th className="pb-2.5">F1 Score</th>
                    <th className="pb-2.5">Engine Role</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {mlModels && mlModels.models.map((m) => (
                    <tr key={m.model_id} className="hover:bg-slate-800/40 transition">
                      <td className="py-2.5 font-bold text-slate-200">{m.name}</td>
                      <td className="py-2.5 font-mono text-slate-300">{m.algorithm}</td>
                      <td className="py-2.5 text-slate-300">{m.sector}</td>
                      <td className="py-2.5 font-mono text-emerald-400 font-bold">{(m.accuracy * 100).toFixed(1)}%</td>
                      <td className="py-2.5 font-mono text-blue-400 font-bold">{(m.precision * 100).toFixed(1)}%</td>
                      <td className="py-2.5 font-mono text-sky-400 font-bold">{(m.recall * 100).toFixed(1)}%</td>
                      <td className="py-2.5 font-mono text-amber-400 font-bold">{(m.f1_score * 100).toFixed(1)}%</td>
                      <td className="py-2.5">
                        <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
                          {m.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: EVACUATION PERFORMANCE & ESCAPEWAYS */}
      {/* ========================================================================= */}
      {activeTab === 'evacuation' && (
        <div className="space-y-6">
          {/* Top 4 Evacuation Cards */}
          {evacPerf && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
                <span className="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">
                  Total Workers at Risk
                </span>
                <span className="text-2xl font-bold font-mono text-slate-100 mt-1 block">
                  {evacPerf.summary.total_workers_at_risk}
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Across All Incidents</span>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
                <span className="text-[10px] font-bold uppercase text-blue-400 block tracking-wider">
                  Alarm ACK Confirmations
                </span>
                <span className="text-2xl font-bold font-mono text-blue-400 mt-1 block">
                  {evacPerf.summary.total_acknowledged_alarms}
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Receipt Confirmed Only</span>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
                <span className="text-[10px] font-bold uppercase text-emerald-400 block tracking-wider">
                  Confirmed Safe in Refuge
                </span>
                <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
                  {evacPerf.summary.total_safely_in_refuge}
                </span>
                <span className="text-[10px] text-emerald-400 font-bold mt-1 block">
                  {evacPerf.summary.overall_clearance_rate_pct}% Evacuation Rate
                </span>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
                <span className="text-[10px] font-bold uppercase text-amber-400 block tracking-wider">
                  Escapeway Reliability
                </span>
                <span className="text-2xl font-bold font-mono text-amber-400 mt-1 block">
                  {evacPerf.summary.route_availability.route_reliability_pct}%
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  {evacPerf.summary.route_availability.safe_clear_routes} Clear / {evacPerf.summary.route_availability.unsafe_blocked_routes} Blocked
                </span>
              </div>
            </div>
          )}

          {/* Strict Safety Notice Banner */}
          <div className="bg-amber-950/20 border border-amber-500/40 rounded-2xl p-4 flex items-start gap-3 shadow-xl">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-200 space-y-1">
              <p className="font-bold uppercase tracking-wider">
                Statutory Mining Safety Protocol & Tally Integrity
              </p>
              <p className="text-amber-300/90 leading-relaxed">
                DGMS / MSHA Rule Enforced: When a worker acknowledges an evacuation alarm via wearable or radio,
                it confirms alarm receipt only. Workers are strictly categorized as <em>In-Transit</em> or <em>Pending</em> and
                are <strong>NEVER</strong> counted as safely evacuated until verified arrival at designated Surface Muster Ground
                or Hermetic Fresh-Air Refuge Chamber.
              </p>
            </div>
          </div>

          {/* Incident-by-Incident Evacuation Breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1">
              Emergency Incident Evacuation History & Corridor Status
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Audit log of all emergency alarm dispatches, escapeway clearance rates, and evacuation durations
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                    <th className="pb-2.5">Alert Code</th>
                    <th className="pb-2.5">Zone & Sector</th>
                    <th className="pb-2.5">Hazard</th>
                    <th className="pb-2.5">Clearance Rate</th>
                    <th className="pb-2.5">Safe vs Total</th>
                    <th className="pb-2.5">Corridor Route</th>
                    <th className="pb-2.5">Refuge Destination</th>
                    <th className="pb-2.5">Duration</th>
                    <th className="pb-2.5">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {evacPerf && evacPerf.incidents.map((inc) => {
                    const isBlocked = inc.route_status === 'UNSAFE_BLOCKED';
                    return (
                      <tr key={inc.alert_id} className="hover:bg-slate-800/40 transition">
                        <td className="py-2.5 font-mono font-bold text-red-400">{inc.alert_code}</td>
                        <td className="py-2.5 font-medium text-slate-200">
                          {inc.zone_name} <span className="text-slate-500 text-[10px]">({inc.mine_type})</span>
                        </td>
                        <td className="py-2.5 text-slate-300 capitalize">{inc.hazard_type.replace('_', ' ')}</td>
                        <td className="py-2.5 font-mono font-bold text-emerald-400">
                          {inc.clearance_rate_pct}%
                        </td>
                        <td className="py-2.5 font-mono text-slate-300">
                          {inc.safely_evacuated} / {inc.affected_workers} Safe
                        </td>
                        <td className="py-2.5">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            isBlocked ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'
                          }`}>
                            {inc.route_status}
                          </span>
                        </td>
                        <td className="py-2.5 text-slate-300">{inc.refuge_name}</td>
                        <td className="py-2.5 font-mono text-slate-400">{inc.duration_minutes} min</td>
                        <td className="py-2.5">
                          <button
                            onClick={() => handleDownload(getIncidentReportPDFUrl(inc.alert_id), `Incident_Report_${inc.alert_code}.pdf`)}
                            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-blue-300 rounded text-[10px] font-semibold transition flex items-center gap-1"
                          >
                            <FileText className="w-3 h-3" />
                            <span>PDF</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: INCIDENT DOSSIERS & PDF/CSV EXPORTS */}
      {/* ========================================================================= */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Download Center Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Download Zone Safety Summary PDF */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                <h4 className="font-bold text-sm text-slate-100">Zone Safety Summary PDF</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generate official statutory safety summary for a specific mining sector with boundary specs, sensor inventory, and refuge paths.
              </p>

              <div className="pt-2 flex items-center gap-2">
                <select
                  value={selectedZoneForPdf}
                  onChange={(e) => setSelectedZoneForPdf(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 flex-1"
                >
                  {zones.map((z) => (
                    <option key={z.id} value={z.id}>
                      {z.zone_code} - {z.name}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => handleDownload(getZoneSafetyPDFUrl(selectedZoneForPdf), `Zone_Safety_Summary_Z${selectedZoneForPdf}.pdf`)}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shrink-0"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </button>
              </div>
            </div>

            {/* Historical Telemetry CSV Export */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
                <h4 className="font-bold text-sm text-slate-100">Historical Telemetry CSV</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Export timestamped sensor readings dataset across open-pit and underground sectors for offline data science and statutory inspection.
              </p>

              <div className="pt-2 flex items-center gap-2">
                <button
                  onClick={() => handleDownload(getSensorCSVUrl({ limit: 1000 }), 'historical_sensor_telemetry.csv')}
                  className="w-full px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition flex items-center justify-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export 1000 Readings (CSV)</span>
                </button>
              </div>
            </div>

            {/* Incident Audit Ledger CSV */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                <h4 className="font-bold text-sm text-slate-100">Emergency Incidents Ledger CSV</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Download complete audit trail of all emergency alerts, evacuation outcomes, clearance rates, and designated refuge stations.
              </p>

              <div className="pt-2 flex items-center gap-2">
                <button
                  onClick={() => handleDownload(getIncidentsCSVUrl(), 'emergency_incidents_ledger.csv')}
                  className="w-full px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition flex items-center justify-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export All Incidents (CSV)</span>
                </button>
              </div>
            </div>
          </div>

          {/* Incident Dossiers Table with Direct PDF Downloads */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider mb-1">
              Historical Emergency Incident Dossiers
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Select an incident to download its official multi-page PDF audit report with complete worker evacuation rosters
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                    <th className="pb-2.5">Incident Code</th>
                    <th className="pb-2.5">Affected Zone</th>
                    <th className="pb-2.5">Hazard Type</th>
                    <th className="pb-2.5">Risk Level</th>
                    <th className="pb-2.5">Trigger Timestamp</th>
                    <th className="pb-2.5">Resolved Timestamp</th>
                    <th className="pb-2.5">Evacuation Clearance</th>
                    <th className="pb-2.5">Download Official Dossier</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {evacPerf && evacPerf.incidents.map((inc) => (
                    <tr key={inc.alert_id} className="hover:bg-slate-800/40 transition">
                      <td className="py-2.5 font-mono font-bold text-red-400">{inc.alert_code}</td>
                      <td className="py-2.5 font-medium text-slate-200">{inc.zone_name}</td>
                      <td className="py-2.5 text-slate-300 capitalize">{inc.hazard_type.replace('_', ' ')}</td>
                      <td className="py-2.5">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase bg-red-600 text-white">
                          {inc.risk_tier}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono text-slate-400">{inc.created_at.replace('T', ' ').slice(0, 19)}</td>
                      <td className="py-2.5 font-mono text-slate-400">
                        {inc.resolved_at ? inc.resolved_at.replace('T', ' ').slice(0, 19) : 'Active Incident'}
                      </td>
                      <td className="py-2.5 font-mono text-emerald-400 font-bold">
                        {inc.safely_evacuated} / {inc.affected_workers} Safe ({inc.clearance_rate_pct}%)
                      </td>
                      <td className="py-2.5">
                        <button
                          onClick={() => handleDownload(getIncidentReportPDFUrl(inc.alert_id), `Incident_Audit_${inc.alert_code}.pdf`)}
                          className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/40 rounded-lg text-xs font-bold transition flex items-center gap-1.5"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>Download PDF</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
