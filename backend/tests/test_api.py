import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

from backend.app.models.database import init_db

@pytest.fixture(autouse=True)
def enable_test_mode(monkeypatch):
    monkeypatch.setattr(settings, "TEST_MODE", True)
    init_db()

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "INCIDENTZERO API"

def test_system_health():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "telemetry_summary" in data

def test_list_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 3
    ids = [s["id"] for s in scenarios]
    assert "scenario_db_regression" in ids
    assert "scenario_memory_leak" in ids
    assert "scenario_dependency_failure" in ids

def test_create_and_get_incident():
    create_payload = {
        "title": "Manual Test Incident",
        "description": "Manual testing incident creation",
        "severity": "SEV2",
        "service": "API Gateway"
    }
    res = client.post("/api/incidents", json=create_payload)
    assert res.status_code == 200
    incident_data = res.json()
    assert incident_data["title"] == "Manual Test Incident"
    inc_id = incident_data["id"]

    # Fetch incident
    res = client.get(f"/api/incidents/{inc_id}")
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == inc_id
    assert fetched["status"] == "TRIGGERED"
