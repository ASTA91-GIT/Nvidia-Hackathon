import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.database import Base, Incident, Investigation, IncidentReport, MetricSnapshot
from backend.app.simulator.environment import ProductionSimulator
from backend.app.agents.commander import IncidentCommander
from backend.app.ai.nebius import DeterministicTestMockProvider

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

@pytest.mark.asyncio
async def test_full_autonomous_investigation_e2e(test_db):
    # 1. Trigger realistic simulated incident
    incident = ProductionSimulator.trigger_incident(test_db, "scenario_db_regression")
    assert incident.status == "TRIGGERED"

    # 2. Initialize Incident Commander with deterministic provider
    provider = DeterministicTestMockProvider()
    events_captured = []
    
    async def capture_event(event):
        events_captured.append(event)

    commander = IncidentCommander(ai_provider=provider, event_broadcaster=capture_event)

    # 3. Execute autonomous multi-agent investigation workflow
    result = await commander.orchestrate_investigation(test_db, incident.id)

    # 4. Verify outcomes
    assert result["status"] == "COMPLETED"
    assert result["recovery_certified"] is True
    assert result["remediation"] == "rollback_deployment"

    # Refresh incident state from db
    test_db.refresh(incident)
    assert incident.status == "RESOLVED"
    assert incident.resolved_at is not None

    # Check post-mortem report was generated
    report = test_db.query(IncidentReport).filter(IncidentReport.incident_id == incident.id).first()
    assert report is not None
    assert "Post-Mortem" in report.title
    assert len(report.root_cause_analysis) > 0
    assert len(report.lessons_learned) > 0

    # Verify event stream transitions were broadcasted
    event_types = [e["event"] for e in events_captured]
    assert "investigation_started" in event_types
    assert "agent_status_change" in event_types
    assert "phase_changed" in event_types
    assert "remediation_executed" in event_types
    assert "investigation_completed" in event_types
