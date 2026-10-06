import React from 'react';
import type { IncidentReport } from '../types';
import { FileText, Download, CheckCircle2, ShieldCheck, Printer, Calendar, Clock, AlertTriangle } from 'lucide-react';

interface IncidentReportViewProps {
  report: IncidentReport | null;
  incidentTitle: string;
}

export const IncidentReportView: React.FC<IncidentReportViewProps> = ({ report, incidentTitle }) => {
  if (!report) {
    return (
      <div className="glass-panel p-10 rounded-2xl border border-cyber-700/60 text-center">
        <FileText className="w-10 h-10 text-slate-500 mx-auto mb-3 animate-pulse" />
        <h3 className="text-sm font-mono font-bold text-slate-200 uppercase mb-1">
          Post-Mortem Incident Report Pending
        </h3>
        <p className="text-xs text-slate-400 font-sans max-w-md mx-auto">
          The Incident Commander autonomously drafts the post-mortem incident report once the Recovery Verification Agent certifies system health restoration.
        </p>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="glass-panel p-6 rounded-2xl border border-cyber-700/70 bg-cyber-900/40 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-infra-emerald text-xs font-mono font-bold uppercase mb-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>INCIDENT RESOLVED & RECOVERY CERTIFIED</span>
          </div>
          <h2 className="text-xl font-bold text-white font-mono">
            {report.title}
          </h2>
          <div className="flex items-center space-x-4 mt-2 text-xs font-mono text-slate-400">
            <span className="flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>{new Date(report.generated_at).toLocaleDateString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5" />
              <span>{new Date(report.generated_at).toLocaleTimeString()} UTC</span>
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-infra-emerald border border-emerald-800 text-[10px]">
              AUTONOMOUS POST-MORTEM
            </span>
          </div>
        </div>

        <button
          onClick={handlePrint}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyber-800 hover:bg-cyber-700 border border-cyber-600 text-xs font-mono font-semibold text-slate-200 transition-all self-start md:self-auto"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Print / Export PDF</span>
        </button>
      </div>

      {/* Main Post-Mortem Document */}
      <div className="glass-panel p-8 rounded-2xl border border-cyber-700/80 space-y-6 bg-cyber-950/80 font-sans text-slate-200">
        {/* Section 1: Executive Summary */}
        <section>
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-emerald border-b border-cyber-800 pb-2 mb-3">
            1. Executive Summary
          </h4>
          <p className="text-xs font-mono leading-relaxed text-slate-300">
            {report.executive_summary}
          </p>
        </section>

        {/* Section 2: Impact Assessment */}
        <section>
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-emerald border-b border-cyber-800 pb-2 mb-3">
            2. Customer & Business Impact Assessment
          </h4>
          <p className="text-xs font-mono leading-relaxed text-slate-300">
            {report.impact_assessment}
          </p>
        </section>

        {/* Section 3: Root Cause Analysis */}
        <section>
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-emerald border-b border-cyber-800 pb-2 mb-3">
            3. Root Cause Technical Analysis
          </h4>
          <div className="bg-cyber-900/60 p-4 rounded-xl border border-cyber-800 text-xs font-mono leading-relaxed text-slate-200">
            {report.root_cause_analysis}
          </div>
        </section>

        {/* Section 4: Remediation & Recovery */}
        <section>
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-emerald border-b border-cyber-800 pb-2 mb-3">
            4. Autonomous Remediation & Telemetry Recovery
          </h4>
          <p className="text-xs font-mono leading-relaxed text-slate-300 mb-3">
            {report.remediation_details}
          </p>
        </section>

        {/* Section 5: Lessons Learned & Action Items */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Lessons Learned */}
          <section className="bg-cyber-900/50 p-4 rounded-xl border border-cyber-800">
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-cyan mb-3">
              5. Lessons Learned
            </h4>
            <ul className="text-xs font-mono text-slate-300 space-y-2">
              {report.lessons_learned?.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-infra-cyan font-bold select-none">•</span>
                  <span>{item}</span>
                </li>
              )) || <li>Automated database schema and index linting must precede merges.</li>}
            </ul>
          </section>

          {/* Preventative Measures */}
          <section className="bg-cyber-900/50 p-4 rounded-xl border border-cyber-800">
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-infra-emerald mb-3">
              6. Preventative Action Items
            </h4>
            <ul className="text-xs font-mono text-slate-300 space-y-2">
              {report.preventative_measures?.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-infra-emerald font-bold select-none">•</span>
                  <span>{item}</span>
                </li>
              )) || <li>Implement automated query execution plan guardrails in PR CI checks.</li>}
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
};
