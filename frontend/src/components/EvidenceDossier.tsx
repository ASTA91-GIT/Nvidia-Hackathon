import React from 'react';
import type { Evidence } from '../types';
import { Terminal, Activity, GitCommit, FileText, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

interface EvidenceDossierProps {
  evidences: Evidence[];
}

export const EvidenceDossier: React.FC<EvidenceDossierProps> = ({ evidences }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'LOG':
        return <Terminal className="w-4 h-4 text-infra-cyan" />;
      case 'METRIC':
        return <Activity className="w-4 h-4 text-infra-emerald" />;
      case 'CODE_DIFF':
      case 'COMMIT':
        return <GitCommit className="w-4 h-4 text-infra-amber" />;
      default:
        return <FileText className="w-4 h-4 text-infra-purple" />;
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'LOG':
        return 'bg-cyan-950/60 text-infra-cyan border-cyan-800/60';
      case 'METRIC':
        return 'bg-emerald-950/60 text-infra-emerald border-emerald-800/60';
      case 'CODE_DIFF':
      case 'COMMIT':
        return 'bg-amber-950/60 text-infra-amber border-amber-800/60';
      default:
        return 'bg-purple-950/60 text-infra-purple border-purple-800/60';
    }
  };

  if (!evidences || evidences.length === 0) {
    return (
      <div className="glass-panel p-8 rounded-xl text-center border border-dashed border-cyber-700/60">
        <Sparkles className="w-8 h-8 text-slate-500 mx-auto mb-2 animate-pulse" />
        <p className="text-xs font-mono text-slate-400">
          Autonomous agents are currently surveying microservices to collect forensic evidence...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
          Correlated Forensic Evidence ({evidences.length} Artifacts)
        </h4>
        <span className="text-[10px] font-mono text-slate-400">
          Ranked by multi-agent confidence score
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {evidences.map((evi) => (
          <div
            key={evi.id}
            className="glass-panel p-4 rounded-xl border border-cyber-700/70 hover:border-cyber-600 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${getBadgeColor(evi.evidence_type)}`}>
                  {getIcon(evi.evidence_type)}
                  <span>{evi.evidence_type}</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400 flex items-center space-x-1">
                  <span>Confidence:</span>
                  <span className="font-bold text-infra-emerald">
                    {Math.round(evi.confidence * 100)}%
                  </span>
                </span>
              </div>

              <h5 className="text-xs font-bold text-white mb-1 font-mono">
                {evi.title}
              </h5>
              <p className="text-[11px] text-slate-300 font-sans leading-relaxed mb-3">
                {evi.description}
              </p>
            </div>

            <div className="pt-2 border-t border-cyber-800/80 flex items-center justify-between text-[10px] font-mono text-slate-400">
              <span>Source: <strong className="text-slate-300">{evi.source_agent}</strong></span>
              <span>{new Date(evi.created_at).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
