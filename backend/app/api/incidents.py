import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.models.database import (
    get_db, Incident, Investigation, AgentRun, Evidence,
    IncidentTimelineEvent, RemediationAction, IncidentReport,
    MetricSnapshot, LogEvent, Deployment
)
from backend.app.models.schemas import (
    IncidentSchema, IncidentCreate, SimulateIncidentRequest,
    EvidenceSchema, AgentRunSchema, IncidentTimelineEventSchema,
    RemediationActionSchema, IncidentReportSchema, RemediateRequest
)
from backend.app.simulator.environment import ProductionSimulator, SERVICES
from backend.app.simulator.scenarios import SCENARIOS
from backend.app.simulator.remediation import RemediationSimulator
from backend.app.agents.commander import IncidentCommander
from backend.app.ai.nebius import get_ai_provider
from backend.app.api.websockets import ws_manager

router = APIRouter(prefix="/api", tags=["incidents"])

@router.get("/system/health")
def get_system_health(db: Session = Depends(get_db)):
    ai_provider = get_ai_provider()
    active_incidents_count = db.query(Incident).filter(Incident.status.in_(["TRIGGERED", "INVESTIGATING", "DIAGNOSED", "REMEDIATING"])).count()
    
    # Calculate average latest metrics
    latest_metrics = db.query(MetricSnapshot).order_by(MetricSnapshot.timestamp.desc()).limit(15).all()
    avg_latency = sum(m.latency_p99_ms for m in latest_metrics) / len(latest_metrics) if latest_metrics else 185.0
    avg_error_rate = sum(m.error_rate_pct for m in latest_metrics) / len(latest_metrics) if latest_metrics else 0.4
    
    return {
        "status": "OPERATIONAL" if active_incidents_count == 0 else "DEGRADED",
        "active_incidents": active_incidents_count,
        "services": SERVICES,
        "ai_provider": {
            "name": ai_provider.__class__.__name__,
            "model": ai_provider.get_model_name(),
            "is_configured": ai_provider.is_configured()
        },
        "telemetry_summary": {
            "latency_p99_ms": round(avg_latency, 1),
            "error_rate_pct": round(avg_error_rate, 2),
            "healthy_services": len(SERVICES) - (1 if active_incidents_count > 0 else 0),
            "total_services": len(SERVICES)
        }
    }

@router.get("/scenarios")
def list_scenarios():
    return ProductionSimulator.get_available_scenarios()

@router.post("/simulate")
async def simulate_incident_global(request: SimulateIncidentRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    incident = ProductionSimulator.trigger_incident(db, scenario_id=request.scenario_id)
    
    await ws_manager.broadcast({
        "event": "incident_triggered",
        "data": {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "service": incident.service
        }
    }, incident_id=incident.id)

    if request.auto_investigate:
        ai_provider = get_ai_provider()
        commander = IncidentCommander(
            ai_provider=ai_provider,
            event_broadcaster=lambda evt: ws_manager.broadcast(evt, incident_id=incident.id)
        )
        background_tasks.add_task(commander.orchestrate_investigation, db, incident.id)

    return {
        "status": "TRIGGERED",
        "incident_id": incident.id,
        "title": incident.title,
        "severity": incident.severity,
        "service": incident.service,
        "auto_investigate": request.auto_investigate
    }

@router.post("/incidents")
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident_id = f"inc-{uuid.uuid4().hex[:8]}"
    incident = Incident(
        id=incident_id,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        service=payload.service,
        scenario_id=payload.scenario_id or "scenario_db_regression",
        status="TRIGGERED"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.started_at.desc()).all()
    results = []
    for inc in incidents:
        inv = db.query(Investigation).filter(Investigation.incident_id == inc.id).order_by(Investigation.started_at.desc()).first()
        results.append({
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "severity": inc.severity,
            "status": inc.status,
            "service": inc.service,
            "scenario_id": inc.scenario_id,
            "started_at": inc.started_at,
            "resolved_at": inc.resolved_at,
            "current_phase": inv.current_phase if inv else None
        })
    return results

@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    investigations = db.query(Investigation).filter(Investigation.incident_id == inc.id).all()
    timeline = db.query(IncidentTimelineEvent).filter(IncidentTimelineEvent.incident_id == inc.id).order_by(IncidentTimelineEvent.timestamp.asc()).all()
    metrics = db.query(MetricSnapshot).filter(MetricSnapshot.incident_id == inc.id).order_by(MetricSnapshot.timestamp.asc()).all()
    logs = db.query(LogEvent).filter(LogEvent.incident_id == inc.id).order_by(LogEvent.timestamp.asc()).all()
    report = db.query(IncidentReport).filter(IncidentReport.incident_id == inc.id).first()

    return {
        "id": inc.id,
        "title": inc.title,
        "description": inc.description,
        "severity": inc.severity,
        "status": inc.status,
        "service": inc.service,
        "scenario_id": inc.scenario_id,
        "started_at": inc.started_at,
        "resolved_at": inc.resolved_at,
        "investigations": investigations,
        "timeline_events": timeline,
        "metrics": metrics,
        "logs": logs,
        "report": report
    }

@router.post("/incidents/{incident_id}/investigate")
async def start_investigation(incident_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    ai_provider = get_ai_provider()
    commander = IncidentCommander(
        ai_provider=ai_provider,
        event_broadcaster=lambda evt: ws_manager.broadcast(evt, incident_id=inc.id)
    )

    background_tasks.add_task(commander.orchestrate_investigation, db, inc.id)

    return {
        "status": "INVESTIGATION_STARTED",
        "incident_id": inc.id,
        "ai_provider_configured": ai_provider.is_configured(),
        "ai_model": ai_provider.get_model_name()
    }

@router.post("/incidents/{incident_id}/simulate")
def simulate_specific_incident(incident_id: str, scenario_id: Optional[str] = None, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Re-apply scenario degradation
    sid = scenario_id or inc.scenario_id or "scenario_db_regression"
    new_inc = ProductionSimulator.trigger_incident(db, sid)
    return {"status": "SIMULATED", "incident_id": new_inc.id}

@router.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    events = db.query(IncidentTimelineEvent).filter(IncidentTimelineEvent.incident_id == incident_id).order_by(IncidentTimelineEvent.timestamp.asc()).all()
    return events

@router.get("/incidents/{incident_id}/evidence")
def get_incident_evidence(incident_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.incident_id == incident_id).order_by(Investigation.started_at.desc()).first()
    if not inv:
        return []
    evidences = db.query(Evidence).filter(Evidence.investigation_id == inv.id).order_by(Evidence.created_at.asc()).all()
    return evidences

@router.get("/incidents/{incident_id}/agents")
def get_incident_agents(incident_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.incident_id == incident_id).order_by(Investigation.started_at.desc()).first()
    if not inv:
        return []
    agents = db.query(AgentRun).filter(AgentRun.investigation_id == inv.id).order_by(AgentRun.started_at.asc()).all()
    return agents

@router.post("/incidents/{incident_id}/remediate")
async def execute_remediation(incident_id: str, payload: RemediateRequest, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    remediation = RemediationSimulator.execute_remediation(
        db=db,
        incident=inc,
        action_type=payload.action_type,
        target_service=payload.target_service,
        parameters=payload.parameters or {},
        proposed_by="Operator Manual Action"
    )

    await ws_manager.broadcast({
        "event": "remediation_executed",
        "data": {
            "incident_id": incident_id,
            "action": payload.action_type,
            "status": remediation.status,
            "result": remediation.result
        }
    }, incident_id=incident_id)

    return remediation

@router.get("/incidents/{incident_id}/report")
def get_incident_report(incident_id: str, db: Session = Depends(get_db)):
    report = db.query(IncidentReport).filter(IncidentReport.incident_id == incident_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Incident post-mortem report not yet generated.")
    return report
