import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Position,
  Handle,
  MarkerType,
} from '@xyflow/react';
import type { Edge, Node } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { AgentRun, Incident } from '../types';
import { ShieldAlert, Terminal, Activity, GitCommit, Search, Brain, Wrench, CheckCircle2 } from 'lucide-react';

interface CommandCenterGraphProps {
  incident: Incident | null;
  agentRuns: AgentRun[];
  onSelectAgent?: (agentName: string) => void;
}

// Custom Node for Graph Visualizer
const PipelineNode = ({ data }: { data: any }) => {
  const getStatusBadge = () => {
    switch (data.status) {
      case 'RUNNING':
        return (
          <span className="flex items-center space-x-1 text-[10px] text-infra-cyan font-mono font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-infra-cyan animate-ping mr-1" />
            ANALYZING
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="flex items-center space-x-1 text-[10px] text-infra-emerald font-mono font-semibold">
            <CheckCircle2 className="w-3 h-3 inline mr-0.5" />
            COMPLETED
          </span>
        );
      case 'FAILED':
        return (
          <span className="text-[10px] text-infra-red font-mono font-semibold">FAILED</span>
        );
      default:
        return (
          <span className="text-[10px] text-slate-500 font-mono">WAITING</span>
        );
    }
  };

  const getBorderClass = () => {
    if (data.status === 'RUNNING') return 'border-infra-cyan ring-1 ring-infra-cyan/50 shadow-lg shadow-cyan-950/40 animate-pulse-slow';
    if (data.status === 'COMPLETED') return 'border-infra-emerald/80 bg-cyber-900/90 shadow-md shadow-emerald-950/30';
    if (data.status === 'FAILED') return 'border-infra-red/80 bg-cyber-900/90';
    return 'border-cyber-700/60 bg-cyber-950/70 opacity-70';
  };

  return (
    <div className={`px-4 py-3 rounded-xl border ${getBorderClass()} min-w-[210px] transition-all duration-300 backdrop-blur-md`}>
      <Handle type="target" position={Position.Left} className="!bg-cyber-600 !w-2 !h-2" />
      <div className="flex items-start justify-between mb-1.5">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded bg-cyber-800 text-slate-200">
            {data.icon}
          </div>
          <span className="text-xs font-bold text-slate-100 font-mono tracking-tight">{data.label}</span>
        </div>
        {getStatusBadge()}
      </div>
      <p className="text-[10px] text-slate-400 font-sans line-clamp-1 mb-1">
        {data.role}
      </p>
      {data.findings && (
        <div className="mt-2 text-[10px] font-mono text-slate-300 bg-cyber-950/80 p-1.5 rounded border border-cyber-800 line-clamp-2">
          {data.findings}
        </div>
      )}
      <Handle type="source" position={Position.Right} className="!bg-cyber-600 !w-2 !h-2" />
    </div>
  );
};

const nodeTypes = {
  pipelineNode: PipelineNode,
};

export const CommandCenterGraph: React.FC<CommandCenterGraphProps> = ({ incident, agentRuns }) => {
  const agentMap = useMemo(() => {
    const map: Record<string, AgentRun> = {};
    agentRuns.forEach((r) => {
      map[r.agent_name] = r;
    });
    return map;
  }, [agentRuns]);

  const nodes: Node[] = useMemo(() => {
    const isTriggered = Boolean(incident);
    const logRun = agentMap['Log Intelligence Agent'];
    const metricsRun = agentMap['Metrics Agent'];
    const codeRun = agentMap['Code Intelligence Agent'];
    const researchRun = agentMap['Research Agent'];
    const rootCauseRun = agentMap['Root Cause Agent'];
    const responseRun = agentMap['Response Agent'];
    const recoveryRun = agentMap['Recovery Verification Agent'];

    return [
      // 1. Incident Trigger Node
      {
        id: 'node-incident',
        type: 'pipelineNode',
        position: { x: 20, y: 160 },
        data: {
          label: 'Incident Detected',
          role: incident ? incident.service : 'Awaiting Incident',
          status: isTriggered ? 'COMPLETED' : 'WAITING',
          findings: incident ? `${incident.severity}: ${incident.title}` : undefined,
          icon: <ShieldAlert className="w-3.5 h-3.5 text-infra-red" />,
        },
      },

      // 2. Specialized Forensic Agents Layer
      {
        id: 'node-log',
        type: 'pipelineNode',
        position: { x: 300, y: 20 },
        data: {
          label: 'Log Agent',
          role: 'Log Cascade & Anomaly Scan',
          status: logRun?.status || (isTriggered ? 'RUNNING' : 'WAITING'),
          findings: logRun?.findings,
          icon: <Terminal className="w-3.5 h-3.5 text-infra-cyan" />,
        },
      },
      {
        id: 'node-metrics',
        type: 'pipelineNode',
        position: { x: 300, y: 120 },
        data: {
          label: 'Metrics Agent',
          role: 'Telemetry & P99 Latency',
          status: metricsRun?.status || 'WAITING',
          findings: metricsRun?.findings,
          icon: <Activity className="w-3.5 h-3.5 text-infra-emerald" />,
        },
      },
      {
        id: 'node-code',
        type: 'pipelineNode',
        position: { x: 300, y: 220 },
        data: {
          label: 'Code Agent',
          role: 'Git Commits & Diff Inspection',
          status: codeRun?.status || 'WAITING',
          findings: codeRun?.findings,
          icon: <GitCommit className="w-3.5 h-3.5 text-infra-amber" />,
        },
      },
      {
        id: 'node-research',
        type: 'pipelineNode',
        position: { x: 300, y: 320 },
        data: {
          label: 'Research Agent',
          role: 'Failure Pattern Research',
          status: researchRun?.status || 'WAITING',
          findings: researchRun?.findings,
          icon: <Search className="w-3.5 h-3.5 text-infra-purple" />,
        },
      },

      // 3. Correlation & Root Cause Diagnosis Node
      {
        id: 'node-root-cause',
        type: 'pipelineNode',
        position: { x: 600, y: 160 },
        data: {
          label: 'Root Cause Agent',
          role: 'Multi-Evidence Correlation',
          status: rootCauseRun?.status || 'WAITING',
          findings: rootCauseRun?.findings,
          icon: <Brain className="w-3.5 h-3.5 text-infra-rose" />,
        },
      },

      // 4. Response & Remediation Node
      {
        id: 'node-response',
        type: 'pipelineNode',
        position: { x: 880, y: 160 },
        data: {
          label: 'Response Agent',
          role: 'Safe Whitelist Remediation',
          status: responseRun?.status || 'WAITING',
          findings: responseRun?.findings,
          icon: <Wrench className="w-3.5 h-3.5 text-infra-amber" />,
        },
      },

      // 5. Recovery Verification Node
      {
        id: 'node-recovery',
        type: 'pipelineNode',
        position: { x: 1160, y: 160 },
        data: {
          label: 'Recovery Agent',
          role: 'Post-Remediation Telemetry Audit',
          status: recoveryRun?.status || (incident?.status === 'RESOLVED' ? 'COMPLETED' : 'WAITING'),
          findings: recoveryRun?.findings || (incident?.status === 'RESOLVED' ? 'Recovery verified. Incident closed.' : undefined),
          icon: <CheckCircle2 className="w-3.5 h-3.5 text-infra-emerald" />,
        },
      },
    ];
  }, [incident, agentMap]);

  const edges: Edge[] = useMemo(() => {
    const makeEdge = (id: string, source: string, target: string, active: boolean) => ({
      id,
      source,
      target,
      animated: active,
      style: {
        stroke: active ? '#10b981' : '#232e42',
        strokeWidth: active ? 2 : 1.5,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: active ? '#10b981' : '#232e42',
      },
    });

    const isTriggered = Boolean(incident);
    const hasEvidence = Boolean(agentMap['Log Intelligence Agent']?.status === 'COMPLETED');
    const hasDiagnosis = Boolean(agentMap['Root Cause Agent']?.status === 'COMPLETED');
    const hasResponse = Boolean(agentMap['Response Agent']?.status === 'COMPLETED');

    return [
      makeEdge('e-inc-log', 'node-incident', 'node-log', isTriggered),
      makeEdge('e-inc-metrics', 'node-incident', 'node-metrics', isTriggered),
      makeEdge('e-inc-code', 'node-incident', 'node-code', isTriggered),
      makeEdge('e-inc-research', 'node-incident', 'node-research', isTriggered),

      makeEdge('e-log-rc', 'node-log', 'node-root-cause', hasEvidence),
      makeEdge('e-metrics-rc', 'node-metrics', 'node-root-cause', hasEvidence),
      makeEdge('e-code-rc', 'node-code', 'node-root-cause', hasEvidence),
      makeEdge('e-research-rc', 'node-research', 'node-root-cause', hasEvidence),

      makeEdge('e-rc-resp', 'node-root-cause', 'node-response', hasDiagnosis),
      makeEdge('e-resp-rec', 'node-response', 'node-recovery', hasResponse),
    ];
  }, [incident, agentMap]);

  return (
    <div className="w-full h-[480px] bg-cyber-950/90 rounded-2xl border border-cyber-700/60 overflow-hidden relative shadow-2xl">
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-2">
        <span className="w-2.5 h-2.5 rounded-full bg-infra-emerald animate-ping" />
        <span className="text-xs font-mono font-semibold uppercase text-slate-300 tracking-wider">
          Multi-Agent Autonomous Orchestration Graph
        </span>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="cyber-grid-bg"
      >
        <Background color="#161e2e" gap={20} size={1} />
        <Controls className="!bg-cyber-900 !border-cyber-700 !text-slate-300 fill-slate-300" />
      </ReactFlow>
    </div>
  );
};
