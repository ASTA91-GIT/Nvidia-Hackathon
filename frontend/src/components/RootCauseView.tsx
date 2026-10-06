import React from 'react';
import { Brain, AlertOctagon, CheckCircle2, ChevronRight, Server, ShieldCheck, Zap } from 'lucide-react';
import type { AgentRun, Evidence } from '../types';

interface RootCauseViewProps {
  rootCauseRun?: AgentRun;
  evidences: Evidence[];
  onNavigateToResponse?: () => void;
}

export const RootCauseView: React.FC<RootCauseViewProps> = ({
  rootCauseRun,
  evidences,
  onNavigateToResponse,
}) => {
  const output = rootCauseRun?.output_payload;
  const isCompleted = rootCauseRun?.status === 'COMPLETED';

  if (!isCompleted || !output) {
    return (
      <div className="glass-panel p-10 rounded-2xl border border-cyber-700/60 text-center">
        <Brain className="w-10 h-10 text-slate-500 mx-auto mb-3 animate-pulse" />
        <h3 className="text-sm font-mono font-bold text-slate-200 uppercase mb-1">
          Root Cause Synthesis Pending
        </h3>
        <p className="text-xs text-slate-400 font-sans max-w-md mx-auto">
          The Root Cause Agent will correlate findings from Log, Metrics, Code, and Research agents once preliminary evidence collection completes.
        </p>
      </div>
    );
  }

  const confidenceScore = Math.round((output.confidence || rootCauseRun.confidence || 0.9) * 100);

  return (
    <div className="space-y-4">
      {/* Primary Diagnosis Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-infra-rose/30 bg-gradient-to-r from-cyber-950 via-cyber-900 to-rose-950/20 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-infra-rose/15 border border-infra-rose/40 text-infra-rose">
              <AlertOctagon className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-infra-rose font-bold">
                AI Inferred Root Cause Diagnosis
              </span>
              <h3 className="text-base font-bold text-white font-mono">
                {output.diagnosis_title || 'Diagnosis Established'}
              </h3>
            </div>
          </div>

          {/* Confidence Meter */}
          <div className="flex items-center space-x-4 bg-cyber-950/80 px-4 py-2.5 rounded-xl border border-cyber-800">
            <div>
              <p className="text-[10px] font-mono text-slate-400 uppercase">Diagnosis Confidence</p>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold font-mono text-infra-emerald">
                  {confidenceScore}%
                </span>
                <span className="text-xs text-infra-emerald font-semibold font-mono">HIGH</span>
              </div>
            </div>
            <div className="w-20 bg-cyber-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-infra-emerald h-full rounded-full transition-all duration-500"
                style={{ width: `${confidenceScore}%` }}
              />
            </div>
          </div>
        </div>

        {/* Detailed Explanation */}
        <div className="bg-cyber-950/80 p-4 rounded-xl border border-cyber-800 mb-4">
          <p className="text-xs font-mono text-slate-200 leading-relaxed">
            {output.probable_root_cause}
          </p>
        </div>

        {/* Originating Service & Factors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-cyber-900/60 p-3.5 rounded-xl border border-cyber-800/80">
            <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1 flex items-center space-x-1">
              <Server className="w-3 h-3 text-infra-cyan" />
              <span>Originating Service</span>
            </span>
            <span className="text-sm font-bold text-white font-mono">
              {output.primary_suspect_service || 'Payment Service'}
            </span>
          </div>

          <div className="bg-cyber-900/60 p-3.5 rounded-xl border border-cyber-800/80">
            <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1">
              Contributing Factors
            </span>
            <ul className="text-xs text-slate-300 font-sans space-y-1">
              {output.contributing_factors?.map((f: string, i: number) => (
                <li key={i} className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-infra-rose" />
                  <span>{f}</span>
                </li>
              )) || <li>Connection pool exhaustion under OLTP load</li>}
            </ul>
          </div>
        </div>

        {/* Call to Action */}
        {onNavigateToResponse && (
          <div className="mt-4 pt-4 border-t border-cyber-800/80 flex justify-end">
            <button
              onClick={onNavigateToResponse}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-infra-emerald hover:bg-emerald-600 text-white font-mono text-xs font-bold transition-all shadow-lg shadow-emerald-950/40"
            >
              <span>Review Safe Remediation Plan</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
