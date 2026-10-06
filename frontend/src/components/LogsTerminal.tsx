import React, { useState } from 'react';
import type { LogEvent } from '../types';
import { Terminal, Search, Filter, ShieldAlert } from 'lucide-react';

interface LogsTerminalProps {
  logs: LogEvent[];
}

export const LogsTerminal: React.FC<LogsTerminalProps> = ({ logs }) => {
  const [filterLevel, setFilterLevel] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const filteredLogs = logs.filter((log) => {
    if (filterLevel !== 'ALL' && log.level !== filterLevel) return false;
    if (searchTerm && !log.message.toLowerCase().includes(searchTerm.toLowerCase()) && !log.service.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  const getLevelStyle = (level: string) => {
    switch (level) {
      case 'ERROR':
      case 'FATAL':
        return 'text-infra-red bg-rose-950/40 border-rose-900/60 font-bold';
      case 'WARN':
        return 'text-infra-amber bg-amber-950/40 border-amber-900/60 font-semibold';
      case 'INFO':
        return 'text-infra-cyan bg-cyan-950/30 border-cyan-900/50';
      default:
        return 'text-slate-400 bg-slate-900/40 border-slate-800';
    }
  };

  return (
    <div className="glass-panel rounded-xl border border-cyber-700/70 overflow-hidden flex flex-col h-80">
      {/* Terminal Toolbar */}
      <div className="bg-cyber-900/90 px-4 py-2 border-b border-cyber-800 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center space-x-2">
          <Terminal className="w-3.5 h-3.5 text-infra-emerald" />
          <span className="font-bold text-slate-200">Live Microservice Log Stream</span>
          <span className="text-[10px] text-slate-500">({filteredLogs.length} events)</span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Level Filter */}
          <div className="flex items-center space-x-1 bg-cyber-950 px-2 py-0.5 rounded border border-cyber-800">
            <Filter className="w-3 h-3 text-slate-400" />
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="bg-transparent text-slate-300 text-[10px] font-mono focus:outline-none cursor-pointer"
            >
              <option value="ALL">ALL LEVELS</option>
              <option value="ERROR">ERROR</option>
              <option value="WARN">WARN</option>
              <option value="INFO">INFO</option>
            </select>
          </div>

          {/* Search Box */}
          <div className="flex items-center space-x-1 bg-cyber-950 px-2 py-0.5 rounded border border-cyber-800">
            <Search className="w-3 h-3 text-slate-400" />
            <input
              type="text"
              placeholder="Filter logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-transparent text-slate-200 text-[10px] font-mono focus:outline-none w-28 placeholder:text-slate-600"
            />
          </div>
        </div>
      </div>

      {/* Terminal Log Output */}
      <div className="flex-1 p-3 overflow-y-auto font-mono text-[11px] space-y-1.5 bg-cyber-950/95 scrollbar-thin">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-10 text-slate-600">
            No log events match the active filter criteria.
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div key={log.id} className="flex items-start space-x-2 py-0.5 hover:bg-cyber-900/50 rounded px-1 group transition-colors">
              <span className="text-slate-500 select-none text-[10px]">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className="text-slate-400 font-semibold min-w-[110px] truncate">
                [{log.service}]
              </span>
              <span className={`px-1.5 py-0.2 rounded text-[9px] border uppercase ${getLevelStyle(log.level)}`}>
                {log.level}
              </span>
              <span className="text-slate-200 flex-1 break-all">
                {log.message}
              </span>
              {log.trace_id && (
                <span className="text-[9px] text-slate-600 group-hover:text-slate-400 transition-colors">
                  {log.trace_id}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
