import uuid
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from backend.app.models.database import (
    Incident, MetricSnapshot, LogEvent, Deployment, IncidentTimelineEvent
)
from backend.app.simulator.scenarios import SCENARIOS

SERVICES = [
    "API Gateway",
    "Payment Service",
    "User Service",
    "Database",
    "Monitoring System"
]

class ProductionSimulator:
    """
    Manages the simulated production environment across 5 microservices:
    - API Gateway
    - Payment Service
    - User Service
    - Database
    - Monitoring System
    """

    @staticmethod
    def get_available_scenarios() -> List[Dict[str, Any]]:
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "description": s["description"],
                "service": s["service"],
                "severity": s["severity"]
            }
            for s in SCENARIOS.values()
        ]

    @staticmethod
    def trigger_incident(db: Session, scenario_id: str = "scenario_db_regression") -> Incident:
        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            scenario = SCENARIOS["scenario_db_regression"]

        incident_id = f"inc-{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.utcnow()

        # 1. Create Incident record
        incident = Incident(
            id=incident_id,
            title=scenario["title"],
            description=scenario["description"],
            severity=scenario["severity"],
            status="TRIGGERED",
            scenario_id=scenario["id"],
            service=scenario["service"],
            started_at=now
        )
        db.add(incident)

        # 2. Add baseline metrics (e.g. 15 mins before incident)
        base = scenario["baseline_metrics"]
        base_time = now - datetime.timedelta(minutes=15)
        for svc in SERVICES:
            # Add realistic baseline metrics per service
            multiplier = 1.0 if svc == scenario["service"] else 0.8
            db.add(MetricSnapshot(
                id=f"met-{uuid.uuid4().hex[:8]}",
                incident_id=incident_id,
                service=svc,
                timestamp=base_time,
                latency_p99_ms=base["latency_p99_ms"] * multiplier,
                latency_p50_ms=base["latency_p50_ms"] * multiplier,
                error_rate_pct=base["error_rate_pct"],
                cpu_usage_pct=base["cpu_usage_pct"] * multiplier,
                memory_usage_pct=base["memory_usage_pct"] * multiplier,
                db_pool_utilization_pct=base["db_pool_utilization_pct"] if svc in ["Database", scenario["service"]] else 10.0,
                stage="BASELINE"
            ))

        # 3. Add incident degraded metrics (at trigger time)
        inc_m = scenario["incident_metrics"]
        for svc in SERVICES:
            # Target service and database receive major degradation
            is_target = (svc == scenario["service"] or svc == "Database" or svc == "API Gateway")
            db.add(MetricSnapshot(
                id=f"met-{uuid.uuid4().hex[:8]}",
                incident_id=incident_id,
                service=svc,
                timestamp=now,
                latency_p99_ms=inc_m["latency_p99_ms"] if is_target else base["latency_p99_ms"],
                latency_p50_ms=inc_m["latency_p50_ms"] if is_target else base["latency_p50_ms"],
                error_rate_pct=inc_m["error_rate_pct"] if is_target else base["error_rate_pct"],
                cpu_usage_pct=inc_m["cpu_usage_pct"] if is_target else base["cpu_usage_pct"],
                memory_usage_pct=inc_m["memory_usage_pct"] if is_target else base["memory_usage_pct"],
                db_pool_utilization_pct=inc_m["db_pool_utilization_pct"] if svc in ["Database", scenario["service"]] else 15.0,
                stage="INCIDENT"
            ))

        # 4. Inject Deployment
        dep_data = scenario["deployment"]
        deployment = Deployment(
            id=f"dep-{uuid.uuid4().hex[:8]}",
            service=dep_data["service"],
            version=dep_data["version"],
            commit_sha=dep_data["commit_sha"],
            commit_message=dep_data["commit_message"],
            author=dep_data["author"],
            deployed_at=now - datetime.timedelta(minutes=8),
            diff_summary=dep_data["diff_summary"],
            code_diff=dep_data["code_diff"]
        )
        db.add(deployment)

        # 5. Inject Logs
        log_start_time = now - datetime.timedelta(minutes=7)
        for idx, log_item in enumerate(scenario["logs"]):
            log_time = log_start_time + datetime.timedelta(seconds=idx * 45)
            db.add(LogEvent(
                id=f"log-{uuid.uuid4().hex[:8]}",
                incident_id=incident_id,
                service=log_item["service"],
                timestamp=log_time,
                level=log_item["level"],
                message=log_item["message"],
                trace_id=f"trc-{uuid.uuid4().hex[:6]}",
                context_data={"scenario_id": scenario["id"]}
            ))

        # 6. Inject Initial Timeline Events
        db.add(IncidentTimelineEvent(
            id=f"time-{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            timestamp=now - datetime.timedelta(minutes=8),
            event_type="DEPLOYMENT",
            title=f"Deployment {dep_data['version']} to {dep_data['service']}",
            description=f"Commit {dep_data['commit_sha']}: {dep_data['commit_message']}",
            source="CI/CD Pipeline"
        ))

        db.add(IncidentTimelineEvent(
            id=f"time-{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            timestamp=now,
            event_type="TRIGGER",
            title=f"Incident Detected: {scenario['title']}",
            description=f"Automated health probes reported severe degradation on {scenario['service']}.",
            source="Monitoring System"
        ))

        db.commit()
        db.refresh(incident)
        return incident
