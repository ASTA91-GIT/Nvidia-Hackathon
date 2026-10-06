import React, { useState } from 'react';
import { Wrench, ShieldCheck, CheckCircle2, AlertTriangle, ArrowRight, RefreshCw, Zap } from 'lucide-react';
import type { AgentRun, RemediationAction } from '../types';

interface ResponseViewProps {
  responseRun?: AgentRun;
  incidentId: string;
  targetService: string;
  onExecuteRemediation: (actionType: string, targetService: string) => Promise<RemediationAction>;
}

export const ResponseView: React.FC<ResponseViewProps> = ({
  responseRun,
  incidentId,
  targetService,
  onExecuteRemediation,
}) => {
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<RemediationAction | null>(null);

  const plan = responseRun?.output_payload;
  const isAvailable = Boolean(plan);

  const actionType = plan?.action_type || 'rollback_deployment';
  const service = plan?.target_service || targetService || 'Payment Service';

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const res = await onExecuteRemediation(actionType, service);
      setExecutionResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setExecuting(false);
    }
  };

  if (!isAvailable) {
    return (
      <div className="glass-panel p-10 rounded-2xl border border-cyber-700/60 text-center">
        <Wrench className="w-10 h-10 text-slate-500 mx-auto mb-3 animate-pulse" />
        <h3 className="text-sm font-mono font-bold text-slate-200 uppercase mb-1">
          Remediation Plan Formulating
        </h3>
        <p className="text-xs text-slate-400 font-sans max-w-md mx-auto">
          The Response Agent evaluates diagnosed root cause mechanisms to synthesize a whitelisted, low-risk remediation strategy.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Response Plan Card */}
      <div className="glass-panel p-6 rounded-2xl border border-cyber-700/70 bg-gradient-to-r from-cyber-950 via-cyber-900 to-amber-950/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-infra-amber/15 border border-infra-amber/40 text-infra-amber">
              <Wrench className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-infra-amber font-bold">
                AI Formulated Remediation Plan
              </span>
              <h3 className="text-base font-bold text-white font-mono capitalize">
                {actionType.replace(/_/g, ' ')}
              </h3>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-md bg-emerald-950 text-infra-emerald border border-emerald-800 text-xs font-mono font-semibold flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 inline mr-1" />
              <span>WHITELISTED ACTION</span>
            </span>
            <span className="px-2.5 py-1 rounded-md bg-cyber-950 text-slate-300 border border-cyber-800 text-xs font-mono">
              Risk: <strong className="text-infra-emerald">{plan.risk_level || 'LOW'}</strong>
            </span>
          </div>
        </div>

        {/* Technical Rationale */}
        <div className="bg-cyber-950/80 p-4 rounded-xl border border-cyber-800 mb-4">
          <h5 className="text-[10px] font-mono uppercase text-slate-400 mb-1">Technical Rationale</h5>
          <p className="text-xs font-mono text-slate-200 leading-relaxed">
            {plan.rationale}
          </p>
        </div>

        {/* Spec details */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <div className="bg-cyber-900/70 p-3 rounded-lg border border-cyber-800">
            <span className="text-[10px] font-mono text-slate-400 block mb-0.5">TARGET SERVICE</span>
            <span className="text-xs font-bold text-white font-mono">{service}</span>
          </div>
          <div className="bg-cyber-900/70 p-3 rounded-lg border border-cyber-800">
            <span className="text-[10px] font-mono text-slate-400 block mb-0.5">ESTIMATED RECOVERY</span>
            <span className="text-xs font-bold text-infra-emerald font-mono">{plan.expected_recovery_time_seconds || 30}s</span>
          </div>
          <div className="bg-cyber-900/70 p-3 rounded-lg border border-cyber-800">
            <span className="text-[10px] font-mono text-slate-400 block mb-0.5">CONTINGENCY FALLBACK</span>
            <span className="text-xs text-slate-300 font-sans line-clamp-1">{plan.rollback_plan || 'Pod Rolling Restart'}</span>
          </div>
        </div>

        {/* Action Trigger Console */}
        <div className="p-4 rounded-xl bg-cyber-950 border border-cyber-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h5 className="text-xs font-bold text-white font-mono flex items-center space-x-1.5">
              <span>Deterministic Execution Environment</span>
            </h5>
            <p className="text-[11px] text-slate-400 font-sans">
              AI proposes; deterministic simulator validates whitelist and executes rollback safely.
            </p>
          </div>

          <button
            onClick={handleExecute}
            disabled={executing || Boolean(executionResult?.status === 'EXECUTED')}
            className={`px-5 py-2.5 rounded-lg font-mono text-xs font-bold flex items-center space-x-2 transition-all ${
              executionResult?.status === 'EXECUTED'
                ? 'bg-emerald-950 text-infra-emerald border border-emerald-800 cursor-default'
                : 'bg-infra-emerald hover:bg-emerald-600 text-white shadow-lg shadow-emerald-950/40 active:scale-95'
            }`}
          >
            {executing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Executing Safe Action...</span>
              </>
            ) : executionResult?.status === 'EXECUTED' ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-infra-emerald" />
                <span>Remediation Executed</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5" />
                <span>Execute Safe Remediation</span>
              </>
            )}
          </button>
        </div>

        {/* Execution Output Banner */}
        {executionResult && (
          <div className="mt-4 p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/80 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center space-x-2 text-infra-emerald">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{executionResult.result?.message || 'Operation executed successfully. Telemetry metrics returning to nominal.'}</span>
            </div>
            <span className="text-[10px] text-slate-400">
              State: {executionResult.result?.new_state || 'POST_REMEDIATION'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
