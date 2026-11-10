import React, { useState, useEffect } from 'react';
import {
  Play,
  Square,
  RotateCcw,
  FastForward,
  AlertTriangle,
  Flame,
  Mountain,
  Wind,
  ShieldCheck,
  Activity,
  Layers,
} from 'lucide-react';
import {
  getSimulationStatus,
  startSimulation,
  stopSimulation,
  resetSimulation,
  setSimulationScenario,
  triggerSimulationTick,
} from '../services/api';
import { wsService } from '../services/websocket';

const SCENARIOS = [
  { id: 'normal', label: 'Normal Baseline', icon: ShieldCheck, color: 'text-emerald-400' },
  { id: 'progressive_drift', label: 'Progressive Drift', icon: Activity, color: 'text-sky-400' },
  { id: 'open_pit_hazard', label: 'Open-Pit Hazard (Slope/Rock)', icon: Mountain, color: 'text-amber-400' },
  { id: 'gas_leak', label: 'Underground Gas Leak (CH4/CO)', icon: Wind, color: 'text-red-400' },
  { id: 'fire_hazard', label: 'Underground Fire (Thermal)', icon: Flame, color: 'text-orange-500' },
];

export default function SimulationControls({ onActionComplete }) {
  const [isRunning, setIsRunning] = useState(false);
  const [scenario, setScenario] = useState('normal');
  const [tickCount, setTickCount] = useState(0);
  const [scenarioTick, setScenarioTick] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Sync simulation status from backend on mount and via WebSocket
  useEffect(() => {
    getSimulationStatus()
      .then((res) => {
        setIsRunning(res.is_running);
        setScenario(res.current_scenario);
        setTickCount(res.tick_count);
        setScenarioTick(res.scenario_tick);
      })
      .catch((err) => console.warn('Could not fetch simulation status:', err));

    const unbind = wsService.on('SIMULATION_STATE', (data) => {
      if (data.is_running !== undefined) setIsRunning(data.is_running);
      if (data.current_scenario) setScenario(data.current_scenario);
      if (data.tick_count !== undefined) setTickCount(data.tick_count);
      if (data.scenario_tick !== undefined) setScenarioTick(data.scenario_tick);
    });

    return () => unbind();
  }, []);

  const handleTogglePlay = async () => {
    setIsProcessing(true);
    try {
      if (isRunning) {
        await stopSimulation();
        setIsRunning(false);
      } else {
        await startSimulation();
        setIsRunning(true);
      }
      if (onActionComplete) onActionComplete();
    } catch (err) {
      console.error('Failed to toggle simulation:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleScenarioChange = async (newScenario) => {
    setIsProcessing(true);
    try {
      await setSimulationScenario(newScenario);
      setScenario(newScenario);
      if (onActionComplete) onActionComplete();
    } catch (err) {
      console.error('Failed to change scenario:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSingleTick = async () => {
    setIsProcessing(true);
    try {
      await triggerSimulationTick();
      if (onActionComplete) onActionComplete();
    } catch (err) {
      console.error('Failed single tick step:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = async () => {
    setIsProcessing(true);
    try {
      await resetSimulation();
      setIsRunning(false);
      setScenario('normal');
      setTickCount(0);
      setScenarioTick(0);
      if (onActionComplete) onActionComplete();
    } catch (err) {
      console.error('Failed to reset simulation:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const activeScenarioObj = SCENARIOS.find((s) => s.id === scenario) || SCENARIOS[0];
  const Icon = activeScenarioObj.icon;

  return (
    <div className="flex flex-wrap items-center gap-2 bg-slate-900/90 border border-slate-800 p-1.5 rounded-xl text-[11px] shadow-lg backdrop-blur">
      {/* Status Badge */}
      <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-950/70 border border-slate-800/80 rounded-lg">
        <span
          className={`w-2 h-2 rounded-full ${
            isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'
          }`}
        />
        <span className="font-semibold text-slate-200">
          {isRunning ? 'SIM RUNNING' : 'SIM PAUSED'}
        </span>
        <span className="text-[10px] text-slate-400 font-mono">
          #{tickCount}
        </span>
      </div>

      {/* Start / Stop Toggle */}
      <button
        onClick={handleTogglePlay}
        disabled={isProcessing}
        className={`px-2.5 py-1 rounded-lg font-medium transition flex items-center gap-1 border ${
          isRunning
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
        } disabled:opacity-50`}
        title={isRunning ? 'Pause simulation loop' : 'Start live continuous simulation loop'}
      >
        {isRunning ? (
          <>
            <Square className="w-3 h-3 fill-current" />
            <span>Pause</span>
          </>
        ) : (
          <>
            <Play className="w-3 h-3 fill-current" />
            <span>Start Loop</span>
          </>
        )}
      </button>

      {/* Manual Step Tick Button */}
      <button
        onClick={handleSingleTick}
        disabled={isProcessing}
        className="px-2 py-1 rounded-lg font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition flex items-center gap-1 border border-slate-700/60 disabled:opacity-50"
        title="Execute a single discrete simulation tick across all sensors and workers"
      >
        <FastForward className="w-3 h-3 text-sky-400" />
        <span>Step 1x</span>
      </button>

      {/* Scenario Dropdown */}
      <div className="flex items-center gap-1 bg-slate-950/70 border border-slate-800 px-2 py-0.5 rounded-lg">
        <Icon className={`w-3.5 h-3.5 ${activeScenarioObj.color}`} />
        <select
          value={scenario}
          onChange={(e) => handleScenarioChange(e.target.value)}
          disabled={isProcessing}
          className="bg-transparent text-slate-200 text-[11px] font-medium outline-none cursor-pointer py-0.5"
          title="Select active physical simulation scenario"
        >
          {SCENARIOS.map((s) => (
            <option key={s.id} value={s.id} className="bg-slate-900 text-slate-200">
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        disabled={isProcessing}
        className="px-2 py-1 rounded-lg font-medium bg-slate-800/80 hover:bg-red-500/20 hover:text-red-300 text-slate-400 transition flex items-center gap-1 border border-slate-700/60 disabled:opacity-50"
        title="Reset simulation, clear active alerts, and restore normal baseline"
      >
        <RotateCcw className="w-3 h-3" />
        <span>Reset</span>
      </button>

      {/* Academic Disclaimer Tag */}
      <span className="hidden xl:inline-block text-[10px] text-slate-300 bg-slate-950/50 border border-slate-800 px-1.5 py-0.5 rounded">
        Synthetic Demo Feed
      </span>
    </div>
  );
}
