from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LogAnomaly(BaseModel):
    service: str
    log_level: str
    message_snippet: str
    frequency_or_impact: str
    relevance: str

class LogAnalysisResult(BaseModel):
    summary: str = Field(..., description="Summary of log analysis across microservices")
    anomalies: List[LogAnomaly] = Field(default_factory=list, description="Key log anomalies identified")
    suspicious_errors: List[str] = Field(default_factory=list, description="Direct error messages indicating failures")
    affected_services: List[str] = Field(default_factory=list, description="List of services experiencing log degradation")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    key_findings: str = Field(..., description="Synthesis of findings for the Incident Commander")

class MetricAnomaly(BaseModel):
    service: str
    metric_name: str
    baseline_value: float
    incident_value: float
    deviation_description: str

class MetricsAnalysisResult(BaseModel):
    summary: str = Field(..., description="High-level metrics degradation summary")
    anomalies: List[MetricAnomaly] = Field(default_factory=list)
    p99_impact: str = Field(..., description="Latency impact assessment")
    error_spike_pct: float = Field(..., description="Observed error rate percentage spike")
    resource_saturation: Dict[str, Any] = Field(default_factory=dict, description="CPU, Memory, or DB Pool saturation indicators")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    key_findings: str = Field(..., description="Key metrics finding synthesis")

class CodeAnalysisResult(BaseModel):
    summary: str = Field(..., description="Summary of code change & deployment analysis")
    commit_sha: Optional[str] = None
    author: Optional[str] = None
    identified_regressions: List[str] = Field(default_factory=list, description="Specific regressions or suspect code changes found in diff")
    risk_assessment: str = Field(..., description="High / Medium / Low risk assessment of commit")
    is_likely_culprit: bool = Field(False, description="Whether the deployment coincides with degradation")
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    key_findings: str = Field(..., description="Key code review findings")

class ResearchResult(BaseModel):
    query: str = Field(..., description="Technical query or error signature searched")
    sources: List[str] = Field(default_factory=list, description="Documentation, CVE, or runbook sources")
    findings: str = Field(..., description="Key technical findings on the error behavior")
    relevance: str = Field(..., description="Why this finding applies to current incident")
    recommendation: str = Field(..., description="Architectural or operational best practice recommendation")

class RootCauseDiagnosis(BaseModel):
    diagnosis_title: str = Field(..., description="Concise title for the root cause diagnosis")
    probable_root_cause: str = Field(..., description="Detailed explanation of the root cause inferred from evidence")
    primary_suspect_service: str = Field(..., description="Primary originating service of the failure")
    contributing_factors: List[str] = Field(default_factory=list, description="Secondary factors aggravating the issue")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="References to log, metric, or code evidence")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Overall diagnosis confidence")
    executive_summary: str = Field(..., description="Executive briefing summary")

class RemediationPlan(BaseModel):
    action_type: str = Field(..., description="Explicit whitelisted action: rollback_deployment, restart_service, or restore_previous_configuration")
    target_service: str = Field(..., description="Target service for remediation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the remediation action")
    risk_level: str = Field("LOW", description="LOW, MEDIUM, or HIGH risk")
    expected_recovery_time_seconds: int = Field(30, description="Estimated seconds for recovery")
    rationale: str = Field(..., description="Technical justification for choosing this remediation")
    rollback_plan: str = Field(..., description="Fallback plan if remediation does not restore service")

class RecoveryVerificationResult(BaseModel):
    is_recovered: bool = Field(..., description="Whether system metrics have returned to nominal baseline")
    latency_delta_ms: float = Field(..., description="Difference between incident latency and post-remediation latency")
    error_rate_delta_pct: float = Field(..., description="Drop in error rate percentage")
    status_assessment: str = Field(..., description="Summary of post-remediation system health")
    remaining_risks: List[str] = Field(default_factory=list, description="Any residual risks or warnings")
    verification_passed: bool = Field(..., description="True if verification passes strict criteria")

class IncidentReportResult(BaseModel):
    title: str = Field(..., description="Incident post-mortem title")
    executive_summary: str = Field(..., description="Executive summary of incident and resolution")
    impact_assessment: str = Field(..., description="Customer and business impact summary")
    root_cause_analysis: str = Field(..., description="Full root cause analysis breakdown")
    remediation_details: str = Field(..., description="Remediation steps executed and outcomes")
    lessons_learned: List[str] = Field(default_factory=list, description="Operational and engineering takeaways")
    preventative_measures: List[str] = Field(default_factory=list, description="Action items to prevent recurrence")
