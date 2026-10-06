import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict

# --- Core Schemas ---

class MetricSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    incident_id: str
    service: str
    timestamp: datetime.datetime
    latency_p99_ms: float
    latency_p50_ms: float
    error_rate_pct: float
    cpu_usage_pct: float
    memory_usage_pct: float
    db_pool_utilization_pct: float = 0.0
    stage: str = "BASELINE"


class LogEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    incident_id: str
    service: str
    timestamp: datetime.datetime
    level: str
    message: str
    trace_id: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class DeploymentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    service: str
    version: str
    commit_sha: str
    commit_message: str
    author: str
    deployed_at: datetime.datetime
    diff_summary: Optional[str] = None
    code_diff: Optional[str] = None


class IncidentTimelineEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    incident_id: str
    timestamp: datetime.datetime
    event_type: str
    title: str
    description: str
    source: str = "System"


class EvidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    investigation_id: str
    source_agent: str
    evidence_type: str
    title: str
    description: str
    data: Optional[Any] = None
    confidence: float = 1.0
    created_at: datetime.datetime


class AgentRunSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    investigation_id: str
    agent_name: str
    agent_role: str
    status: str
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    findings: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None
    output_payload: Optional[Dict[str, Any]] = None


class RemediationActionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    incident_id: str
    action_type: str
    target_service: str
    parameters: Optional[Dict[str, Any]] = None
    status: str = "PENDING"
    risk_level: str = "LOW"
    proposed_by: str = "Response Agent"
    executed_at: Optional[datetime.datetime] = None
    result: Optional[Dict[str, Any]] = None


class IncidentReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    incident_id: str
    title: str
    executive_summary: str
    impact_assessment: str
    root_cause_analysis: str
    evidence_summary: Optional[List[Dict[str, Any]]] = None
    remediation_details: str
    recovery_metrics: Optional[Dict[str, Any]] = None
    lessons_learned: Optional[List[str]] = None
    preventative_measures: Optional[List[str]] = None
    generated_at: datetime.datetime


class InvestigationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    status: str
    current_phase: str
    started_at: datetime.datetime
    ended_at: Optional[datetime.datetime] = None
    summary: Optional[str] = None
    agent_runs: List[AgentRunSchema] = []
    evidences: List[EvidenceSchema] = []


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "SEV1"
    service: str = "Payment Service"
    scenario_id: Optional[str] = "scenario_db_regression"


class IncidentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    scenario_id: Optional[str] = None
    service: str
    started_at: datetime.datetime
    resolved_at: Optional[datetime.datetime] = None
    investigations: List[InvestigationSchema] = []
    timeline_events: List[IncidentTimelineEventSchema] = []


class SimulateIncidentRequest(BaseModel):
    scenario_id: str = Field("scenario_db_regression", description="ID of the scenario to simulate")
    auto_investigate: bool = Field(True, description="Whether to automatically start investigation upon triggering")


class RemediateRequest(BaseModel):
    action_type: str = Field(..., description="Allowed action: rollback_deployment, restart_service, restore_previous_configuration")
    target_service: str
    parameters: Optional[Dict[str, Any]] = None
