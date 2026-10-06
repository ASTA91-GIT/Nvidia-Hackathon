export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'SEV0' | 'SEV1' | 'SEV2' | 'SEV3';
  status: 'TRIGGERED' | 'INVESTIGATING' | 'DIAGNOSED' | 'REMEDIATING' | 'REMEDIATED' | 'VERIFYING' | 'RESOLVED';
  service: string;
  scenario_id?: string;
  started_at: string;
  resolved_at?: string;
  current_phase?: string;
  investigations?: Investigation[];
  timeline_events?: TimelineEvent[];
  metrics?: MetricSnapshot[];
  logs?: LogEvent[];
  report?: IncidentReport;
}

export interface Investigation {
  id: string;
  incident_id: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'PAUSED_UNCONFIGURED';
  current_phase: string;
  started_at: string;
  ended_at?: string;
  summary?: string;
  agent_runs: AgentRun[];
  evidences: Evidence[];
}

export interface AgentRun {
  id: string;
  investigation_id: string;
  agent_name: string;
  agent_role: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  started_at: string;
  completed_at?: string;
  findings?: string;
  confidence?: number;
  error_message?: string;
  output_payload?: any;
}

export interface Evidence {
  id: string;
  investigation_id: string;
  source_agent: string;
  evidence_type: 'LOG' | 'METRIC' | 'CODE_DIFF' | 'COMMIT' | 'DOC' | 'DIAGNOSIS' | 'RESPONSE_PLAN' | 'RECOVERY';
  title: string;
  description: string;
  data?: any;
  confidence: number;
  created_at: string;
}

export interface MetricSnapshot {
  id: string;
  incident_id: string;
  service: string;
  timestamp: string;
  latency_p99_ms: number;
  latency_p50_ms: number;
  error_rate_pct: number;
  cpu_usage_pct: number;
  memory_usage_pct: number;
  db_pool_utilization_pct: number;
  stage: 'BASELINE' | 'INCIDENT' | 'POST_REMEDIATION';
}

export interface LogEvent {
  id: string;
  incident_id: string;
  service: string;
  timestamp: string;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
  message: string;
  trace_id?: string;
  context_data?: any;
}

export interface TimelineEvent {
  id: string;
  incident_id: string;
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  source: string;
}

export interface RemediationAction {
  id: string;
  incident_id: string;
  action_type: string;
  target_service: string;
  parameters?: any;
  status: 'PENDING' | 'APPROVED' | 'EXECUTED' | 'FAILED';
  risk_level: string;
  proposed_by: string;
  executed_at?: string;
  result?: any;
}

export interface IncidentReport {
  id: string;
  incident_id: string;
  title: string;
  executive_summary: string;
  impact_assessment: string;
  root_cause_analysis: string;
  evidence_summary?: any[];
  remediation_details: string;
  recovery_metrics?: any;
  lessons_learned?: string[];
  preventative_measures?: string[];
  generated_at: string;
}

export interface SystemHealth {
  status: 'OPERATIONAL' | 'DEGRADED';
  active_incidents: number;
  services: string[];
  ai_provider: {
    name: string;
    model: string;
    is_configured: boolean;
  };
  telemetry_summary: {
    latency_p99_ms: number;
    error_rate_pct: number;
    healthy_services: number;
    total_services: number;
  };
}

export interface Scenario {
  id: string;
  title: string;
  description: string;
  service: string;
  severity: string;
}
