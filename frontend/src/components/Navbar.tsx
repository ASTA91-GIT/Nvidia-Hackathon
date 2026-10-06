import React from 'react';
import { ShieldAlert, Cpu, Activity, Play, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { SystemHealth } from '../types';

interface NavbarProps {
  health: SystemHealth | null;
  onOpenSimulateModal: () => void;
  activeView: string;
  setActiveView: (view: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  onOpenSimulateModal,
  activeView,
  setActiveView,
}) => {
  const isAiConfigured = health?.ai_provider?.is_configured ?? false;

  return (
    <header className="sticky top-0 z-50 border-b border-cyber-700/60 bg-cyber-950/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Identity */}
        <div className="flex items-center space-x-6">
          <div 
            onClick={() => setActiveView('dashboard')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-lg bg-infra-emerald/10 border border-infra-emerald/40 flex items-center justify-center group-hover:border-infra-emerald transition-colors shadow-sm">
              <ShieldAlert className="w-5 h-5 text-infra-emerald animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold tracking-wider text-white font-mono">
                  INCIDENT<span className="text-infra-emerald">ZERO</span>
                </span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-infra-emerald/15 text-infra-emerald border border-infra-emerald/30 font-semibold">
                  v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono tracking-tight">
                Autonomous AI Incident Commander
              </p>
            </div>
          </div>

          {/* Navigation tabs */}
          <nav className="hidden md:flex items-center space-x-1 pl-4 border-l border-cyber-700/50">
            <button
              onClick={() => setActiveView('dashboard')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium font-mono transition-all ${
                activeView === 'dashboard'
                  ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
              }`}
            >
              System Operations
            </button>
            <button
              onClick={() => setActiveView('incidents')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium font-mono transition-all ${
                activeView === 'incidents'
                  ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
              }`}
            >
              Incidents Dossier
            </button>
          </nav>
        </div>

        {/* Center / Right Telemetry & Actions */}
        <div className="flex items-center space-x-4">
          {/* AI Model Badge */}
          <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-cyber-900/90 border border-cyber-700/70 text-xs font-mono">
            <Cpu className="w-3.5 h-3.5 text-infra-cyan" />
            <span className="text-slate-400">NVIDIA Nemotron:</span>
            {isAiConfigured ? (
              <span className="inline-flex items-center text-infra-emerald font-semibold space-x-1">
                <span className="w-2 h-2 rounded-full bg-infra-emerald animate-ping" />
                <span>Nebius Live</span>
              </span>
            ) : (
              <span className="inline-flex items-center text-infra-amber font-semibold space-x-1">
                <AlertTriangle className="w-3 h-3 text-infra-amber inline mr-1" />
                <span>AI Provider Unconfigured</span>
              </span>
            )}
          </div>

          {/* System Health Status */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-cyber-900/90 border border-cyber-700/70 text-xs font-mono">
            <Activity className="w-3.5 h-3.5 text-infra-emerald" />
            <span className="text-slate-400">P99:</span>
            <span className="text-white font-bold">
              {health?.telemetry_summary ? `${health.telemetry_summary.latency_p99_ms}ms` : '185ms'}
            </span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">Err:</span>
            <span className={`font-bold ${
              (health?.telemetry_summary?.error_rate_pct ?? 0) > 5 ? 'text-infra-red' : 'text-infra-emerald'
            }`}>
              {health?.telemetry_summary ? `${health.telemetry_summary.error_rate_pct}%` : '0.4%'}
            </span>
          </div>

          {/* Simulate Incident Button */}
          <button
            id="btn-simulate-incident"
            onClick={onOpenSimulateModal}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-infra-rose via-infra-red to-orange-600 hover:from-rose-600 hover:to-orange-700 text-white font-medium text-xs font-mono uppercase tracking-wider shadow-lg shadow-infra-rose/20 hover:shadow-infra-rose/40 transition-all border border-rose-500/30 active:scale-95"
          >
            <Zap className="w-3.5 h-3.5 fill-current animate-bounce" />
            <span>Simulate Incident</span>
          </button>
        </div>
      </div>
    </header>
  );
};
