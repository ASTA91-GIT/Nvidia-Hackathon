import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, 
    DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from backend.app.config import settings

Base = declarative_base()

def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, default="SEV1")  # SEV0, SEV1, SEV2, SEV3
    status = Column(String, default="TRIGGERED")  # TRIGGERED, INVESTIGATING, DIAGNOSED, REMEDIATING, VERIFYING, RESOLVED
    scenario_id = Column(String, nullable=True)  # e.g. "scenario_db_regression"
    service = Column(String, default="Payment Service")
    started_at = Column(DateTime, default=now_utc)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    investigations = relationship("Investigation", back_populates="incident", cascade="all, delete-orphan")
    timeline_events = relationship("IncidentTimelineEvent", back_populates="incident", cascade="all, delete-orphan")
    metric_snapshots = relationship("MetricSnapshot", back_populates="incident", cascade="all, delete-orphan")
    log_events = relationship("LogEvent", back_populates="incident", cascade="all, delete-orphan")
    remediations = relationship("RemediationAction", back_populates="incident", cascade="all, delete-orphan")
    report = relationship("IncidentReport", back_populates="incident", uselist=False, cascade="all, delete-orphan")


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    status = Column(String, default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, FAILED
    current_phase = Column(String, default="COLLECTING_EVIDENCE") # DETECT, INVESTIGATE, CORRELATE, ROOT_CAUSE, RESPONSE, RECOVERY
    started_at = Column(DateTime, default=now_utc)
    ended_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    
    incident = relationship("Incident", back_populates="investigations")
    agent_runs = relationship("AgentRun", back_populates="investigation", cascade="all, delete-orphan")
    evidences = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=False)
    agent_name = Column(String, nullable=False)  # Commander, Log, Metrics, Code, Research, RootCause, Response, Recovery
    agent_role = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, default=now_utc)
    completed_at = Column(DateTime, nullable=True)
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    findings = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    investigation = relationship("Investigation", back_populates="agent_runs")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, index=True)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=False)
    source_agent = Column(String, nullable=False)  # Log Intelligence, Metrics Agent, etc.
    evidence_type = Column(String, nullable=False)  # LOG, METRIC, CODE_DIFF, COMMIT, DOC
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=now_utc)

    investigation = relationship("Investigation", back_populates="evidences")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    service = Column(String, nullable=False)
    timestamp = Column(DateTime, default=now_utc)
    latency_p99_ms = Column(Float, nullable=False)
    latency_p50_ms = Column(Float, nullable=False)
    error_rate_pct = Column(Float, nullable=False)
    cpu_usage_pct = Column(Float, nullable=False)
    memory_usage_pct = Column(Float, nullable=False)
    db_pool_utilization_pct = Column(Float, default=0.0)
    stage = Column(String, default="BASELINE")  # BASELINE, INCIDENT, POST_REMEDIATION

    incident = relationship("Incident", back_populates="metric_snapshots")


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    service = Column(String, nullable=False)
    timestamp = Column(DateTime, default=now_utc)
    level = Column(String, default="INFO")  # DEBUG, INFO, WARN, ERROR, FATAL
    message = Column(Text, nullable=False)
    trace_id = Column(String, nullable=True)
    context_data = Column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="log_events")


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, index=True)
    service = Column(String, nullable=False)
    version = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    commit_message = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    deployed_at = Column(DateTime, default=now_utc)
    diff_summary = Column(Text, nullable=True)
    code_diff = Column(Text, nullable=True)


class IncidentTimelineEvent(Base):
    __tablename__ = "incident_timeline_events"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    timestamp = Column(DateTime, default=now_utc)
    event_type = Column(String, nullable=False)  # TRIGGER, AGENT_ACTION, DIAGNOSIS, REMEDIATION, RECOVERY
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String, default="System")

    incident = relationship("Incident", back_populates="timeline_events")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    action_type = Column(String, nullable=False)  # rollback_deployment, restart_service, restore_previous_configuration
    target_service = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String, default="PENDING")  # PENDING, APPROVED, EXECUTED, FAILED
    risk_level = Column(String, default="LOW")  # LOW, MEDIUM, HIGH
    proposed_by = Column(String, default="Response Agent")
    executed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="remediations")


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), unique=True, nullable=False)
    title = Column(String, nullable=False)
    executive_summary = Column(Text, nullable=False)
    impact_assessment = Column(Text, nullable=False)
    root_cause_analysis = Column(Text, nullable=False)
    evidence_summary = Column(JSON, nullable=True)
    remediation_details = Column(Text, nullable=False)
    recovery_metrics = Column(JSON, nullable=True)
    lessons_learned = Column(JSON, nullable=True)
    preventative_measures = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=now_utc)

    incident = relationship("Incident", back_populates="report")


# Database engine & session maker
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
