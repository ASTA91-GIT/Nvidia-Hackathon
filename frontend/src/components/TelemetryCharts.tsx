import React from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import type { MetricSnapshot } from '../types';

interface TelemetryChartsProps {
  metrics: MetricSnapshot[];
}

export const TelemetryCharts: React.FC<TelemetryChartsProps> = ({ metrics }) => {
  // Sort metrics and aggregate by stage and service
  const formattedData = metrics.map((m, idx) => ({
    time: `T+${idx * 2}m`,
    stage: m.stage,
    service: m.service,
    p99: Math.round(m.latency_p99_ms),
    p50: Math.round(m.latency_p50_ms),
    errorRate: Number(m.error_rate_pct.toFixed(1)),
    cpu: Number(m.cpu_usage_pct.toFixed(1)),
    dbPool: Number(m.db_pool_utilization_pct.toFixed(1)),
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-cyber-900 border border-cyber-700 p-3 rounded-lg shadow-xl font-mono text-xs">
          <p className="text-slate-400 font-semibold mb-1">{label} ({payload[0]?.payload?.stage})</p>
          {payload.map((entry: any, index: number) => (
            <div key={`item-${index}`} className="flex justify-between space-x-4 my-0.5">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="font-bold text-white">
                {entry.value} {entry.name.includes('Rate') ? '%' : entry.name.includes('Latency') ? 'ms' : '%'}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* P99 / P50 Latency Chart */}
      <div className="glass-panel p-4 rounded-xl border border-cyber-700/60">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              Latency Telemetry (P99 & P50)
            </h4>
            <p className="text-[10px] text-slate-400">Response time degradation during incident & recovery</p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-infra-rose/10 text-infra-rose border border-infra-rose/20">
            Threshold: 500ms
          </span>
        </div>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={formattedData}>
              <defs>
                <linearGradient id="p99Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="p50Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#161e2e" />
              <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
              <YAxis stroke="#475569" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 10, fontFamily: 'monospace' }} />
              <Area type="monotone" dataKey="p99" name="Latency P99 (ms)" stroke="#ef4444" fillOpacity={1} fill="url(#p99Grad)" strokeWidth={2} />
              <Area type="monotone" dataKey="p50" name="Latency P50 (ms)" stroke="#3b82f6" fillOpacity={1} fill="url(#p50Grad)" strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Error Rate & DB Pool Saturation Chart */}
      <div className="glass-panel p-4 rounded-xl border border-cyber-700/60">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              Error Rate & DB Pool Saturation
            </h4>
            <p className="text-[10px] text-slate-400">Connection starvation and HTTP 5xx error percentage</p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-infra-amber/10 text-infra-amber border border-infra-amber/20">
            Pool Max: 100
          </span>
        </div>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#161e2e" />
              <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
              <YAxis stroke="#475569" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 10, fontFamily: 'monospace' }} />
              <Bar dataKey="errorRate" name="Error Rate (%)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="dbPool" name="DB Pool Saturation (%)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
