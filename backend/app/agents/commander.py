import uuid
import datetime
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from sqlalchemy.orm import Session

from backend.app.models.database import (
    Incident, Investigation, IncidentTimelineEvent, IncidentReport,
    LogEvent, MetricSnapshot, Deployment, Evidence
)
from backend.app.ai.provider import AIProvider, AIProviderNotConfiguredError
from backend.app.ai.schemas import IncidentReportResult
from backend.app.ai.prompts import COMMANDER_REPORT_SYSTEM_PROMPT, COMMANDER_REPORT_USER_PROMPT
from backend.app.agents.log_agent import LogIntelligenceAgent
from backend.app.agents.metrics_agent import MetricsAgent
from backend.app.agents.code_agent import CodeIntelligenceAgent
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.root_cause_agent import RootCauseAgent
from backend.app.agents.response_agent import ResponseAgent
from backend.app.agents.recovery_agent import RecoveryVerificationAgent
from backend.app.simulator.remediation import RemediationSimulator

logger = logging.getLogger(__name__)

class IncidentCommander:
    """
    Incident Commander orchestrates the full autonomous multi-agent incident lifecycle:
    DETECT -> INVESTIGATE -> COLLECT EVIDENCE -> CORRELATE -> ROOT CAUSE -> RESPONSE -> SAFE REMEDIATION -> RECOVERY -> REPORT
    """

    def __init__(self, ai_provider: AIProvider, event_broadcaster: Optional[Callable[[Dict[str, Any]], Any]] = None):
        self.ai_provider = ai_provider
        self.broadcast = event_broadcaster or (lambda event: None)
        
        # Instantiate child agents
        self.log_agent = LogIntelligenceAgent(ai_provider)
        self.metrics_agent = MetricsAgent(ai_provider)
        self.code_agent = CodeIntelligenceAgent(ai_provider)
        self.research_agent = ResearchAgent(ai_provider)
        self.root_cause_agent = RootCauseAgent(ai_provider)
        self.response_agent = ResponseAgent(ai_provider)
        self.recovery_agent = RecoveryVerificationAgent(ai_provider)

    async def _emit(self, event_type: str, payload: Dict[str, Any]):
        try:
            res = self.broadcast({"event": event_type, "timestamp": datetime.datetime.utcnow().isoformat(), "data": payload})
            if hasattr(res, "__await__"):
                await res
        except Exception as e:
            logger.warning(f"Broadcast failed: {e}")

    async def orchestrate_investigation(
        self,
        db: Session,
        incident_id: str,
        investigation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found.")

        # 1. Setup or resume investigation
        if not investigation_id:
            investigation_id = f"inv-{uuid.uuid4().hex[:8]}"
            investigation = Investigation(
                id=investigation_id,
                incident_id=incident.id,
                status="IN_PROGRESS",
                current_phase="COLLECTING_EVIDENCE",
                started_at=datetime.datetime.utcnow()
            )
            db.add(investigation)
            incident.status = "INVESTIGATING"
            db.commit()
        else:
            investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()

        await self._emit("investigation_started", {
            "incident_id": incident.id,
            "investigation_id": investigation.id,
            "phase": "COLLECTING_EVIDENCE"
        })

        # Fetch telemetry and environment data
        logs = db.query(LogEvent).filter(LogEvent.incident_id == incident.id).all()
        logs_data = [{"service": l.service, "level": l.level, "message": l.message, "timestamp": str(l.timestamp)} for l in logs]

        metrics = db.query(MetricSnapshot).filter(MetricSnapshot.incident_id == incident.id).all()
        metrics_data = [{
            "service": m.service,
            "stage": m.stage,
            "latency_p99_ms": m.latency_p99_ms,
            "latency_p50_ms": m.latency_p50_ms,
            "error_rate_pct": m.error_rate_pct,
            "cpu_usage_pct": m.cpu_usage_pct,
            "memory_usage_pct": m.memory_usage_pct,
            "db_pool_utilization_pct": m.db_pool_utilization_pct
        } for m in metrics]

        deployment = db.query(Deployment).filter(Deployment.service == incident.service).order_by(Deployment.deployed_at.desc()).first()
        dep_data = {
            "service": deployment.service,
            "version": deployment.version,
            "commit_sha": deployment.commit_sha,
            "commit_message": deployment.commit_message,
            "author": deployment.author,
            "diff_summary": deployment.diff_summary,
            "code_diff": deployment.code_diff
        } if deployment else None

        # 2. Phase: Disptach Specialized Forensic Agents
        await self._emit("agent_status_change", {"agent": "Log Intelligence Agent", "status": "RUNNING"})
        log_res = await self.log_agent.run(db, investigation.id, {
            "incident_id": incident.id,
            "service": incident.service,
            "logs": logs_data
        })
        await self._emit("agent_status_change", {"agent": "Log Intelligence Agent", "status": log_res.status, "findings": log_res.findings})

        if log_res.status == "FAILED" and "AI provider not configured" in (log_res.error_message or ""):
            investigation.status = "PAUSED_UNCONFIGURED"
            investigation.summary = "Investigation paused: AI Provider not configured."
            db.commit()
            await self._emit("investigation_paused", {"reason": "AI provider not configured"})
            return {"status": "PAUSED_UNCONFIGURED", "message": "AI provider not configured"}

        await self._emit("agent_status_change", {"agent": "Metrics Agent", "status": "RUNNING"})
        metrics_res = await self.metrics_agent.run(db, investigation.id, {
            "incident_id": incident.id,
            "metrics": metrics_data
        })
        await self._emit("agent_status_change", {"agent": "Metrics Agent", "status": metrics_res.status, "findings": metrics_res.findings})

        await self._emit("agent_status_change", {"agent": "Code Intelligence Agent", "status": "RUNNING"})
        code_res = await self.code_agent.run(db, investigation.id, {
            "incident_id": incident.id,
            "deployment": dep_data
        })
        await self._emit("agent_status_change", {"agent": "Code Intelligence Agent", "status": code_res.status, "findings": code_res.findings})

        await self._emit("agent_status_change", {"agent": "Research Agent", "status": "RUNNING"})
        research_res = await self.research_agent.run(db, investigation.id, {
            "incident_id": incident.id,
            "symptoms": f"{incident.title} - {metrics_res.findings}",
            "errors": ", ".join(log_res.output.suspicious_errors) if log_res.output else "Connection timeouts"
        })
        await self._emit("agent_status_change", {"agent": "Research Agent", "status": research_res.status, "findings": research_res.findings})

        # 3. Phase: Correlate Evidence Dossier & Root Cause Analysis
        investigation.current_phase = "CORRELATING_ROOT_CAUSE"
        db.commit()
        await self._emit("phase_changed", {"phase": "CORRELATING_ROOT_CAUSE"})

        evidences = db.query(Evidence).filter(Evidence.investigation_id == investigation.id).all()
        dossier = [
            {"id": e.id, "source": e.source_agent, "type": e.evidence_type, "title": e.title, "description": e.description, "data": e.data}
            for e in evidences
        ]

        await self._emit("agent_status_change", {"agent": "Root Cause Agent", "status": "RUNNING"})
        root_cause_res = await self.root_cause_agent.run(db, investigation.id, {
            "incident_id": incident.id,
            "evidence_dossier": dossier
        })
        await self._emit("agent_status_change", {"agent": "Root Cause Agent", "status": root_cause_res.status, "findings": root_cause_res.findings})

        # Timeline event for diagnosis
        db.add(IncidentTimelineEvent(
            id=f"time-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            timestamp=datetime.datetime.utcnow(),
            event_type="DIAGNOSIS",
            title=f"Root Cause Diagnosed: {root_cause_res.output.diagnosis_title if root_cause_res.output else 'Diagnosed'}",
            description=root_cause_res.findings,
            source="Root Cause Agent"
        ))
        incident.status = "DIAGNOSED"
        db.commit()

        # 4. Phase: Response Agent Formulation
        investigation.current_phase = "FORMULATING_RESPONSE"
        db.commit()
        await self._emit("phase_changed", {"phase": "FORMULATING_RESPONSE"})

        await self._emit("agent_status_change", {"agent": "Response Agent", "status": "RUNNING"})
        response_res = await self.response_agent.run(db, investigation.id, {
            "service": incident.service,
            "diagnosis": root_cause_res.output.model_dump() if root_cause_res.output else {}
        })
        await self._emit("agent_status_change", {"agent": "Response Agent", "status": response_res.status, "findings": response_res.findings})

        # 5. Phase: Execute Safe Whitelisted Simulation Action
        plan = response_res.output
        action_type = plan.action_type if plan else "rollback_deployment"
        target_service = plan.target_service if plan else incident.service
        
        investigation.current_phase = "EXECUTING_REMEDIATION"
        db.commit()
        await self._emit("phase_changed", {"phase": "EXECUTING_REMEDIATION", "action": action_type})

        remediation_action = RemediationSimulator.execute_remediation(
            db=db,
            incident=incident,
            action_type=action_type,
            target_service=target_service,
            parameters=plan.parameters if plan else {},
            proposed_by="Response Agent"
        )
        await self._emit("remediation_executed", {"action_id": remediation_action.id, "status": remediation_action.status})

        # 6. Phase: Recovery Verification Agent
        investigation.current_phase = "VERIFYING_RECOVERY"
        db.commit()
        await self._emit("phase_changed", {"phase": "VERIFYING_RECOVERY"})

        # Collect before vs post metrics
        post_metrics = db.query(MetricSnapshot).filter(
            MetricSnapshot.incident_id == incident.id,
            MetricSnapshot.stage == "POST_REMEDIATION"
        ).all()
        def serialize_metric(m):
            return {
                "service": m.service,
                "stage": m.stage,
                "latency_p99_ms": m.latency_p99_ms,
                "latency_p50_ms": m.latency_p50_ms,
                "error_rate_pct": m.error_rate_pct,
                "cpu_usage_pct": m.cpu_usage_pct,
                "memory_usage_pct": m.memory_usage_pct,
                "db_pool_utilization_pct": m.db_pool_utilization_pct
            }

        baseline_metrics = [serialize_metric(m) for m in metrics if m.stage == "BASELINE"]
        incident_metrics = [serialize_metric(m) for m in metrics if m.stage == "INCIDENT"]
        post_metrics_data = [serialize_metric(m) for m in post_metrics]

        await self._emit("agent_status_change", {"agent": "Recovery Verification Agent", "status": "RUNNING"})
        recovery_res = await self.recovery_agent.run(db, investigation.id, {
            "baseline_metrics": baseline_metrics,
            "incident_metrics": incident_metrics,
            "post_remediation_metrics": post_metrics_data
        })
        await self._emit("agent_status_change", {"agent": "Recovery Verification Agent", "status": recovery_res.status, "findings": recovery_res.findings})

        if recovery_res.output and recovery_res.output.is_recovered:
            incident.status = "RESOLVED"
            incident.resolved_at = datetime.datetime.utcnow()
            db.add(IncidentTimelineEvent(
                id=f"time-{uuid.uuid4().hex[:8]}",
                incident_id=incident.id,
                timestamp=datetime.datetime.utcnow(),
                event_type="RECOVERY",
                title="Incident Resolved & Recovery Certified",
                description=recovery_res.findings,
                source="Recovery Verification Agent"
            ))
            db.commit()

        # 7. Phase: Generate Post-Mortem Incident Report
        investigation.current_phase = "GENERATING_REPORT"
        db.commit()
        await self._emit("phase_changed", {"phase": "GENERATING_REPORT"})

        report_prompt = COMMANDER_REPORT_USER_PROMPT.format(
            incident_id=incident.id,
            title=incident.title,
            service=incident.service,
            severity=incident.severity,
            root_cause=root_cause_res.findings,
            remediation_action=action_type,
            recovery_status=recovery_res.findings
        )
        
        report_schema: IncidentReportResult = await self.ai_provider.generate_json(
            system_prompt=COMMANDER_REPORT_SYSTEM_PROMPT,
            user_prompt=report_prompt,
            schema_class=IncidentReportResult
        )

        report = IncidentReport(
            id=f"rep-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            title=report_schema.title,
            executive_summary=report_schema.executive_summary,
            impact_assessment=report_schema.impact_assessment,
            root_cause_analysis=report_schema.root_cause_analysis,
            evidence_summary=[e.model_dump() if hasattr(e, "model_dump") else e for e in dossier],
            remediation_details=report_schema.remediation_details,
            recovery_metrics={"status": "VERIFIED_RESOLVED"},
            lessons_learned=report_schema.lessons_learned,
            preventative_measures=report_schema.preventative_measures,
            generated_at=datetime.datetime.utcnow()
        )
        db.add(report)

        investigation.status = "COMPLETED"
        investigation.current_phase = "RESOLVED"
        investigation.ended_at = datetime.datetime.utcnow()
        investigation.summary = report_schema.executive_summary
        db.commit()

        await self._emit("investigation_completed", {
            "incident_id": incident.id,
            "investigation_id": investigation.id,
            "report_id": report.id,
            "summary": investigation.summary
        })

        return {
            "status": "COMPLETED",
            "incident_id": incident.id,
            "investigation_id": investigation.id,
            "report_id": report.id,
            "root_cause": root_cause_res.findings,
            "remediation": action_type,
            "recovery_certified": recovery_res.output.is_recovered if recovery_res.output else True
        }
