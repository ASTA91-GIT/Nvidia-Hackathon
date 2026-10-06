import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.database import Base, Incident, Investigation, AgentRun, Evidence
from backend.app.ai.nebius import DeterministicTestMockProvider
from backend.app.agents.log_agent import LogIntelligenceAgent
from backend.app.agents.metrics_agent import MetricsAgent
from backend.app.agents.code_agent import CodeIntelligenceAgent
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.root_cause_agent import RootCauseAgent
from backend.app.agents.response_agent import ResponseAgent
from backend.app.agents.recovery_agent import RecoveryVerificationAgent

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
async def test_log_intelligence_agent(test_db):
    provider = DeterministicTestMockProvider()
    agent = LogIntelligenceAgent(provider)
    
    # Create mock investigation
    inv = Investigation(id="inv-test-1", incident_id="inc-1", status="IN_PROGRESS")
    test_db.add(inv)
    test_db.commit()

    result = await agent.run(test_db, inv.id, {
        "incident_id": "inc-1",
        "service": "Payment Service",
        "logs": [{"service": "Database", "level": "ERROR", "message": "Max connections reached"}]
    })

    assert result.status == "COMPLETED"
    assert result.confidence >= 0.9
    assert result.output is not None
    assert len(result.output.anomalies) > 0

    # Verify agent run & evidence persisted in database
    run_record = test_db.query(AgentRun).filter(AgentRun.investigation_id == inv.id).first()
    assert run_record is not None
    assert run_record.agent_name == "Log Intelligence Agent"
    assert run_record.status == "COMPLETED"

    evidence_record = test_db.query(Evidence).filter(Evidence.investigation_id == inv.id).first()
    assert evidence_record is not None
    assert evidence_record.evidence_type == "LOG"

@pytest.mark.asyncio
async def test_root_cause_agent(test_db):
    provider = DeterministicTestMockProvider()
    agent = RootCauseAgent(provider)
    
    inv = Investigation(id="inv-test-2", incident_id="inc-2", status="IN_PROGRESS")
    test_db.add(inv)
    test_db.commit()

    result = await agent.run(test_db, inv.id, {
        "incident_id": "inc-2",
        "evidence_dossier": [{"title": "DB Exhaustion", "type": "LOG"}]
    })

    assert result.status == "COMPLETED"
    assert result.output.probable_root_cause is not None
    assert result.output.confidence >= 0.8
