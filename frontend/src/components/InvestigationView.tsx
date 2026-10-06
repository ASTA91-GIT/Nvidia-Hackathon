import React, { useState } from 'react';
import type { Incident, AgentRun, Evidence, MetricSnapshot, LogEvent, IncidentReport, RemediationAction } from '../types';
import { CommandCenterGraph } from './CommandCenterGraph';
import { EvidenceDossier } from './EvidenceDossier';
import { TelemetryCharts } from './TelemetryCharts';
import { LogsTerminal } from './LogsTerminal';
import { RootCauseView } from './RootCauseView';
import { ResponseView } from './ResponseView';
import { IncidentReportView } from './IncidentReportView';
import {
  ShieldAlert, Activity, FileText, Brain, Wrench, CheckCircle2,
  Clock, ArrowLeft, RefreshCw, AlertTriangle, Layers, GitCommit
} from 'lucide-react';

interface InvestigationViewProps {
  incident: Incident;
  agentRuns: AgentRun[];
  evidences: Evidence[];
  metrics: MetricSnapshot[];
  logs: LogEvent[];
  report: IncidentReport | null;
  onBack: () => void;
  onStartInvestigation: () => Promise<void>;
  onExecuteRemediation: (actionType: string, targetService: string) => Promise<RemediationAction>;
}

export const InvestigationView: React.FC<InvestigationViewProps> = ({
  incident,
  agentRuns,
  evidences,
  metrics,
  logs,
  report,
  onBack,
  onStartInvestigation,
  onExecuteRemediation,
}) => {
  const [activeTab, setActiveTab] = useState<'graph' | 'evidence' | 'telemetry' | 'logs' | 'root_cause' | 'response' | 'report'>('graph');
  const [investigating, setInvestigating] = useState(false);

  const rootCauseRun = agentRuns.find((r) => r.agent_name === 'Root Cause Agent');
  const responseRun = agentRuns.find((r) => r.agent_name === 'Response Agent');

  const handleInvestigateClick = async () => {
    setInvestigating(true);
    try {
      await onStartInvestigation();
    } finally {
      setInvestigating(false);
    }
  };

  const stages = [
    { key: 'DETECT', label: 'Detect' },
    { key: 'INVESTIGATE', label: 'Investigate' },
    { key: 'EVIDENCE', label: 'Collect Evidence' },
    { key: 'CORRELATE', label: 'Correlate' },
    { key: 'ROOT_CAUSE', label: 'Root Cause' },
    { key: 'RESPONSE', label: 'Response' },
    { key: 'REMEDIATION', label: 'Remediation' },
    { key: 'RECOVERY', label: 'Verify Recovery' },
    { key: 'REPORT', label: 'Incident Report' },
  ];

  const getStageIndex = () => {
    if (incident.status === 'RESOLVED') return 8;
    if (incident.status === 'VERIFYING') return 7;
    if (incident.status === 'REMEDIATED') return 6;
    if (incident.status === 'REMEDIATING') return 5;
    if (incident.status === 'DIAGNOSED') return 4;
    if (incident.status === 'INVESTIGATING') return 2;
    return 0;
  };

  const currentStageIdx = getStageIndex();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Incident Header & Lifecycle Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-cyber-700/80 bg-cyber-950/90 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="p-2 rounded-xl bg-cyber-900 border border-cyber-800 text-slate-400 hover:text-white hover:bg-cyber-800 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center space-x-3 mb-1">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-infra-rose border border-rose-800 font-bold">
                  {incident.severity}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  Target: <strong className="text-white">{incident.service}</strong>
                </span>
                <span className="text-xs font-mono text-slate-500">ID: {incident.id}</span>
              </div>
              <h1 className="text-lg font-bold text-white font-mono">
                {incident.title}
              </h1>
            </div>
          </div>

          {/* Action Trigger if pending */}
          <div className="flex items-center space-x-3">
            {incident.status === 'TRIGGERED' && (
              <button
                onClick={handleInvestigateClick}
                disabled={investigating}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-infra-emerald hover:bg-emerald-600 text-white font-mono text-xs font-bold shadow-lg shadow-emerald-950/40 transition-all active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${investigating ? 'animate-spin' : ''}`} />
                <span>{investigating ? 'Dispatching Agents...' : 'Start Autonomous Investigation'}</span>
              </button>
            )}
            <div className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-bold uppercase ${
              incident.status === 'RESOLVED'
                ? 'bg-emerald-950/60 text-infra-emerald border-emerald-800'
                : 'bg-rose-950/60 text-infra-rose border-rose-800'
            }`}>
              Status: {incident.status}
            </div>
          </div>
        </div>

        {/* Linear Stage Progress Pipeline */}
        <div className="pt-2 border-t border-cyber-800/80">
          <div className="hidden sm:flex items-center justify-between relative">
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-cyber-800 -translate-y-1/2 z-0" />
            {stages.map((stage, idx) => {
              const isPast = idx < currentStageIdx;
              const isCurrent = idx === currentStageIdx;
              return (
                <div key={stage.key} className="flex flex-col items-center relative z-10">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all ${
                    isPast
                      ? 'bg-infra-emerald text-cyber-950'
                      : isCurrent
                      ? 'bg-infra-cyan text-cyber-950 ring-4 ring-cyan-950 animate-pulse'
                      : 'bg-cyber-900 border border-cyber-700 text-slate-500'
                  }`}>
                    {idx + 1}
                  </div>
                  <span className={`text-[10px] font-mono mt-1 ${
                    isCurrent ? 'text-infra-cyan font-bold' : isPast ? 'text-slate-300' : 'text-slate-600'
                  }`}>
                    {stage.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="flex items-center space-x-1 border-b border-cyber-800 pb-2 overflow-x-auto scrollbar-none">
        <button
          onClick={() => setActiveTab('graph')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'graph'
              ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Multi-Agent Graph</span>
        </button>

        <button
          onClick={() => setActiveTab('evidence')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'evidence'
              ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Evidence Dossier ({evidences.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('telemetry')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'telemetry'
              ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Telemetry Charts</span>
        </button>

        <button
          onClick={() => setActiveTab('logs')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'logs'
              ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Log Terminal ({logs.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('root_cause')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'root_cause'
              ? 'bg-cyber-800 text-infra-rose border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <Brain className="w-3.5 h-3.5" />
          <span>Root Cause Diagnosis</span>
        </button>

        <button
          onClick={() => setActiveTab('response')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'response'
              ? 'bg-cyber-800 text-infra-amber border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <Wrench className="w-3.5 h-3.5" />
          <span>Safe Remediation</span>
        </button>

        <button
          onClick={() => setActiveTab('report')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-mono font-semibold transition-all shrink-0 ${
            activeTab === 'report'
              ? 'bg-cyber-800 text-infra-emerald border border-cyber-600'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-900'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Post-Mortem Report</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {activeTab === 'graph' && (
          <CommandCenterGraph
            incident={incident}
            agentRuns={agentRuns}
          />
        )}

        {activeTab === 'evidence' && (
          <EvidenceDossier evidences={evidences} />
        )}

        {activeTab === 'telemetry' && (
          <TelemetryCharts metrics={metrics} />
        )}

        {activeTab === 'logs' && (
          <LogsTerminal logs={logs} />
        )}

        {activeTab === 'root_cause' && (
          <RootCauseView
            rootCauseRun={rootCauseRun}
            evidences={evidences}
            onNavigateToResponse={() => setActiveTab('response')}
          />
        )}

        {activeTab === 'response' && (
          <ResponseView
            responseRun={responseRun}
            incidentId={incident.id}
            targetService={incident.service}
            onExecuteRemediation={onExecuteRemediation}
          />
        )}

        {activeTab === 'report' && (
          <IncidentReportView
            report={report}
            incidentTitle={incident.title}
          />
        )}
      </div>
    </div>
  );
};
