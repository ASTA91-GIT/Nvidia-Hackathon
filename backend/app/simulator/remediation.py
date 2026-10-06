import uuid
import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.database import (
    Incident, MetricSnapshot, LogEvent, RemediationAction, IncidentTimelineEvent
)
from backend.app.simulator.scenarios import SCENARIOS

ALLOWED_REMEDIATION_ACTIONS = {
    "rollback_deployment": {
        "description": "Roll back the most recent service deployment to the previous stable artifact.",
        "allowed_services": ["Payment Service", "API Gateway", "User Service"]
    },
    "restart_service": {
        "description": "Perform a rolling restart of service container pods to flush corrupted state or heap memory.",
        "allowed_services": ["Payment Service", "API Gateway", "User Service", "Database"]
    },
    "restore_previous_configuration": {
        "description": "Revert runtime configuration / feature flags to previous known-good baseline.",
        "allowed_services": ["Payment Service", "API Gateway", "User Service", "Monitoring System"]
    }
}

class RemediationSimulator:
    """
    Validates and simulates safe execution of whitelisted remediation operations.
    Enforces that arbitrary shell commands or untrusted scripts are NEVER executed.
    """

    @staticmethod
    def validate_action(action_type: str, target_service: str) -> Tuple[bool, str]:
        if action_type not in ALLOWED_REMEDIATION_ACTIONS:
            return False, f"Action '{action_type}' is forbidden. Allowed actions: {list(ALLOWED_REMEDIATION_ACTIONS.keys())}"
        
        rule = ALLOWED_REMEDIATION_ACTIONS[action_type]
        if target_service not in rule["allowed_services"]:
            return False, f"Action '{action_type}' cannot be executed against '{target_service}'. Allowed services: {rule['allowed_services']}"

        return True, "Valid action"

    @staticmethod
    def execute_remediation(
        db: Session,
        incident: Incident,
        action_type: str,
        target_service: str,
        parameters: Dict[str, Any] = None,
        proposed_by: str = "Response Agent"
    ) -> RemediationAction:
        is_valid, msg = RemediationSimulator.validate_action(action_type, target_service)
        now = datetime.datetime.utcnow()

        remediation = RemediationAction(
            id=f"rem-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            action_type=action_type,
            target_service=target_service,
            parameters=parameters or {},
            proposed_by=proposed_by,
            executed_at=now
        )

        if not is_valid:
            remediation.status = "FAILED"
            remediation.result = {"error": msg, "success": False}
            db.add(remediation)
            db.commit()
            db.refresh(remediation)
            return remediation

        # Valid action executed in simulator
        remediation.status = "EXECUTED"
        scenario = SCENARIOS.get(incident.scenario_id, SCENARIOS["scenario_db_regression"])
        rec_m = scenario["recovery_metrics"]

        # Record timeline event
        db.add(IncidentTimelineEvent(
            id=f"time-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            timestamp=now,
            event_type="REMEDIATION",
            title=f"Executed Remediation: {action_type.replace('_', ' ').title()}",
            description=f"Action applied to {target_service}. Verifying system health and recovery metrics...",
            source=proposed_by
        ))

        # Add recovery log events
        db.add(LogEvent(
            id=f"log-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            service=target_service,
            timestamp=now + datetime.timedelta(seconds=5),
            level="INFO",
            message=f"Remediation operation '{action_type}' successfully applied to {target_service} cluster.",
            trace_id=f"rem-{uuid.uuid4().hex[:6]}"
        ))

        db.add(LogEvent(
            id=f"log-{uuid.uuid4().hex[:8]}",
            incident_id=incident.id,
            service="Monitoring System",
            timestamp=now + datetime.timedelta(seconds=15),
            level="INFO",
            message=f"Health probe check: Latency returning to nominal baseline. Error rate below threshold.",
            trace_id=f"rem-{uuid.uuid4().hex[:6]}"
        ))

        # Add recovery metric snapshots
        services = ["API Gateway", "Payment Service", "User Service", "Database", "Monitoring System"]
        for svc in services:
            multiplier = 1.0 if svc == target_service else 0.8
            db.add(MetricSnapshot(
                id=f"met-{uuid.uuid4().hex[:8]}",
                incident_id=incident.id,
                service=svc,
                timestamp=now + datetime.timedelta(seconds=30),
                latency_p99_ms=rec_m["latency_p99_ms"] * multiplier,
                latency_p50_ms=rec_m["latency_p50_ms"] * multiplier,
                error_rate_pct=rec_m["error_rate_pct"],
                cpu_usage_pct=rec_m["cpu_usage_pct"] * multiplier,
                memory_usage_pct=rec_m["memory_usage_pct"] * multiplier,
                db_pool_utilization_pct=rec_m["db_pool_utilization_pct"] if svc in ["Database", target_service] else 12.0,
                stage="POST_REMEDIATION"
            ))

        incident.status = "REMEDIATED"
        remediation.result = {
            "success": True,
            "message": f"Remediation '{action_type}' successfully executed against {target_service}.",
            "new_state": "POST_REMEDIATION"
        }

        db.add(remediation)
        db.commit()
        db.refresh(remediation)
        return remediation
