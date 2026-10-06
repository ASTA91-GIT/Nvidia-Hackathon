import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.database import Base, Incident, MetricSnapshot, LogEvent, Deployment
from backend.app.simulator.environment import ProductionSimulator
from backend.app.simulator.remediation import RemediationSimulator, ALLOWED_REMEDIATION_ACTIONS

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()

def test_trigger_incident_creates_telemetry(test_db):
    incident = ProductionSimulator.trigger_incident(test_db, "scenario_db_regression")
    assert incident.id is not None
    assert incident.status == "TRIGGERED"
    assert incident.severity == "SEV1"

    # Verify metrics snapshots were generated (baseline + incident)
    metrics = test_db.query(MetricSnapshot).filter(MetricSnapshot.incident_id == incident.id).all()
    assert len(metrics) > 0
    stages = set(m.stage for m in metrics)
    assert "BASELINE" in stages
    assert "INCIDENT" in stages

    # Check P99 latency degraded in incident stage
    incident_p99 = [m.latency_p99_ms for m in metrics if m.stage == "INCIDENT" and m.service == "Payment Service"][0]
    baseline_p99 = [m.latency_p99_ms for m in metrics if m.stage == "BASELINE" and m.service == "Payment Service"][0]
    assert incident_p99 > 5000.0
    assert baseline_p99 < 300.0

    # Verify logs were injected
    logs = test_db.query(LogEvent).filter(LogEvent.incident_id == incident.id).all()
    assert len(logs) >= 5
    levels = set(l.level for l in logs)
    assert "ERROR" in levels or "WARN" in levels

def test_remediation_whitelist_validation():
    # Valid action
    is_valid, msg = RemediationSimulator.validate_action("rollback_deployment", "Payment Service")
    assert is_valid is True

    # Invalid action
    is_valid, msg = RemediationSimulator.validate_action("rm_rf_slash", "Payment Service")
    assert is_valid is False
    assert "forbidden" in msg.lower()

    # Invalid service
    is_valid, msg = RemediationSimulator.validate_action("rollback_deployment", "NonExistentService")
    assert is_valid is False

def test_remediation_execution_and_metrics_recovery(test_db):
    incident = ProductionSimulator.trigger_incident(test_db, "scenario_db_regression")
    rem = RemediationSimulator.execute_remediation(
        test_db,
        incident,
        action_type="rollback_deployment",
        target_service="Payment Service"
    )
    assert rem.status == "EXECUTED"
    assert incident.status == "REMEDIATED"

    # Check POST_REMEDIATION metrics
    post_metrics = test_db.query(MetricSnapshot).filter(
        MetricSnapshot.incident_id == incident.id,
        MetricSnapshot.stage == "POST_REMEDIATION"
    ).all()
    assert len(post_metrics) > 0
    p99 = [m.latency_p99_ms for m in post_metrics if m.service == "Payment Service"][0]
    assert p99 < 300.0  # Successfully recovered
