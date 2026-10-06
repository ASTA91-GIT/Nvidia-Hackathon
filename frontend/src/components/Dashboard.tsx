import React from 'react';
import type { Incident, SystemHealth, Scenario } from '../types';
import {
  Activity, AlertTriangle, ShieldCheck, Zap, Database, Server, Clock,
  ArrowRight, ShieldAlert, Cpu, CheckCircle2, ChevronRight
} from 'lucide-react';

interface DashboardProps {
  health: SystemHealth | null;
  incidents: Incident[];
  onSelectIncident: (id: string) => void;
  onOpenSimulateModal: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  health,
  incidents,
  onSelectIncident,
  onOpenSimulateModal,
}) => {
  const activeIncidents = incidents.filter(
    (inc) => inc.status !== 'RESOLVED'
  );
  const resolvedIncidents = incidents.filter(
    (inc) => inc.status === 'RESOLVED'
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner & Quick Trigger */}
      <div className="glass-panel p-6 rounded-2xl border border-cyber-700/80 bg-gradient-to-r from-cyber-950 via-cyber-900 to-cyber-850 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-[10px] font-mono uppercase text-infra-emerald font-bold tracking-wider mb-1">
            <span className="w-2 h-2 rounded-full bg-infra-emerald animate-pulse" />
            <span>NVIDIA × Nebius Global AI Hackathon Edition</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white font-mono tracking-tight">
            Autonomous Incident Command Center
          </h1>
          <p className="text-xs text-slate-400 font-sans mt-1 max-w-2xl">
            Real-time multi-agent reasoning platform powered by NVIDIA Nemotron on Nebius Token Factory.
            Detects architectural anomalies, correlates log and metric telemetry, and executes safe remediations.
          </p>
        </div>

        <button
          onClick={onOpenSimulateModal}
          className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-gradient-to-r from-infra-rose via-infra-red to-orange-600 hover:from-rose-600 hover:to-orange-700 text-white font-mono text-xs font-bold uppercase tracking-wider shadow-xl shadow-rose-950/50 hover:shadow-rose-900/60 active:scale-95 transition-all self-start md:self-auto"
        >
          <Zap className="w-4 h-4 fill-current animate-bounce" />
          <span>Simulate Production Incident</span>
        </button>
      </div>

      {/* Primary Telemetry Metric KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* P99 Latency Card */}
        <div className="glass-panel p-4 rounded-xl border border-cyber-700/60 hover:border-cyber-600 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              Gateway P99 Latency
            </span>
            <Activity className="w-4 h-4 text-infra-cyan" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">
              {health?.telemetry_summary ? `${health.telemetry_summary.latency_p99_ms}ms` : '185.0ms'}
            </span>
            <span className={`text-[10px] font-mono font-semibold ${
              (health?.telemetry_summary?.latency_p99_ms ?? 185) > 500 ? 'text-infra-red' : 'text-infra-emerald'
            }`}>
              {(health?.telemetry_summary?.latency_p99_ms ?? 185) > 500 ? '▲ CRITICAL' : '▼ NOMINAL'}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 font-sans mt-1">Normal baseline: &lt;200ms</p>
        </div>

        {/* Global Error Rate Card */}
        <div className="glass-panel p-4 rounded-xl border border-cyber-700/60 hover:border-cyber-600 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              HTTP Error Rate (5xx)
            </span>
            <AlertTriangle className="w-4 h-4 text-infra-rose" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className={`text-2xl font-bold font-mono ${
              (health?.telemetry_summary?.error_rate_pct ?? 0) > 2 ? 'text-infra-red' : 'text-white'
            }`}>
              {health?.telemetry_summary ? `${health.telemetry_summary.error_rate_pct}%` : '0.4%'}
            </span>
            <span className={`text-[10px] font-mono font-semibold ${
              (health?.telemetry_summary?.error_rate_pct ?? 0) > 2 ? 'text-infra-red' : 'text-infra-emerald'
            }`}>
              {(health?.telemetry_summary?.error_rate_pct ?? 0) > 2 ? '▲ SPIKE' : 'STABLE'}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 font-sans mt-1">SLA budget: &lt;1.0%</p>
        </div>

        {/* Microservices Health Card */}
        <div className="glass-panel p-4 rounded-xl border border-cyber-700/60 hover:border-cyber-600 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              Active Mesh Services
            </span>
            <Server className="w-4 h-4 text-infra-emerald" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">
              {health?.telemetry_summary ? `${health.telemetry_summary.healthy_services}/${health.telemetry_summary.total_services}` : '5/5'}
            </span>
            <span className="text-[10px] font-mono font-semibold text-infra-emerald">
              HEALTHY
            </span>
          </div>
          <p className="text-[10px] text-slate-500 font-sans mt-1">Gateway, Payment, User, DB, Monitor</p>
        </div>

        {/* Active Incidents Card */}
        <div className="glass-panel p-4 rounded-xl border border-cyber-700/60 hover:border-cyber-600 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              Active Investigations
            </span>
            <ShieldAlert className="w-4 h-4 text-infra-amber" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className={`text-2xl font-bold font-mono ${
              activeIncidents.length > 0 ? 'text-infra-amber' : 'text-white'
            }`}>
              {activeIncidents.length}
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              ({resolvedIncidents.length} Resolved)
            </span>
          </div>
          <p className="text-[10px] text-slate-500 font-sans mt-1">Autonomous dispatch enabled</p>
        </div>
      </div>

      {/* Incidents Management Table */}
      <div className="glass-panel rounded-2xl border border-cyber-700/80 overflow-hidden shadow-xl">
        <div className="px-6 py-4 bg-cyber-900/80 border-b border-cyber-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-infra-emerald" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              Live Incidents & Investigation Queue
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            {incidents.length} total recorded
          </span>
        </div>

        <div className="divide-y divide-cyber-800/80 bg-cyber-950/60">
          {incidents.length === 0 ? (
            <div className="p-12 text-center">
              <ShieldCheck className="w-10 h-10 text-infra-emerald mx-auto mb-3" />
              <h4 className="text-sm font-mono font-bold text-slate-300">
                All Production Services Operating Nominally
              </h4>
              <p className="text-xs text-slate-500 font-sans mt-1 max-w-sm mx-auto mb-4">
                No active incidents detected. Click the button below to inject a simulated failure.
              </p>
              <button
                onClick={onOpenSimulateModal}
                className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyber-800 hover:bg-cyber-700 border border-cyber-600 text-xs font-mono font-semibold text-slate-200 transition-all"
              >
                <Zap className="w-3.5 h-3.5 text-infra-rose" />
                <span>Simulate First Incident</span>
              </button>
            </div>
          ) : (
            incidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc.id)}
                className="p-4 hover:bg-cyber-900/80 cursor-pointer transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg border shrink-0 mt-0.5 ${
                    inc.status === 'RESOLVED'
                      ? 'bg-emerald-950/60 border-emerald-800 text-infra-emerald'
                      : 'bg-rose-950/60 border-rose-800 text-infra-rose'
                  }`}>
                    {inc.status === 'RESOLVED' ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 animate-pulse" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-infra-rose border border-rose-900 font-semibold">
                        {inc.severity}
                      </span>
                      <span className="text-xs font-mono font-bold text-white group-hover:text-infra-emerald transition-colors">
                        {inc.title}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-sans line-clamp-1 mb-1">
                      {inc.description}
                    </p>
                    <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-500">
                      <span>Service: <strong className="text-slate-400">{inc.service}</strong></span>
                      <span>•</span>
                      <span>Phase: <strong className="text-infra-cyan">{inc.current_phase || inc.status}</strong></span>
                      <span>•</span>
                      <span>{new Date(inc.started_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <span className={`px-2.5 py-1 rounded-md text-[10px] font-mono font-bold uppercase border ${
                    inc.status === 'RESOLVED'
                      ? 'bg-emerald-950/60 text-infra-emerald border-emerald-800/80'
                      : inc.status === 'INVESTIGATING'
                      ? 'bg-cyan-950/60 text-infra-cyan border-cyan-800/80 animate-pulse'
                      : 'bg-amber-950/60 text-infra-amber border-amber-800/80'
                  }`}>
                    {inc.status}
                  </span>
                  <div className="p-1.5 rounded-lg bg-cyber-900 group-hover:bg-cyber-800 text-slate-400 group-hover:text-white transition-colors">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
