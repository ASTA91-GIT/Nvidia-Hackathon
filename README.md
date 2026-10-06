# INCIDENTZERO 🛡️
### Autonomous AI Incident Commander

**Built for the NVIDIA × Nebius Global AI Hackathon**

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2-61dafb.svg)](https://react.dev/)
[![NVIDIA Nemotron](https://img.shields.io/badge/AI-NVIDIA%20Nemotron-76b900.svg)](https://build.nvidia.com/)
[![Nebius Token Factory](https://img.shields.io/badge/Platform-Nebius%20Token%20Factory-8a2be2.svg)](https://nebius.com/)

---

## 🚀 Project Vision

**IncidentZero** is an autonomous AI incident-response platform that investigates complex simulated production outages across microservices. Instead of requiring human on-call engineers to manually correlate disparate monitoring dashboards, logs, and Git commits during an outage, IncidentZero dispatches a fleet of specialized AI agents coordinated by an **Incident Commander**.

### The Autonomous Investigation Pipeline:
```
DETECT ➔ INVESTIGATE ➔ COLLECT EVIDENCE ➔ CORRELATE ➔ ROOT CAUSE ➔ RESPONSE ➔ SAFE REMEDIATION ➔ VERIFY RECOVERY ➔ GENERATE REPORT
```

---

## 🧠 Multi-Agent Architecture

IncidentZero separates forensic investigation into discrete, specialized agent responsibilities with strictly typed Pydantic contracts:

1. **Incident Commander (Orchestrator):** Manages the investigation state machine, coordinates child agents, streams real-time updates over WebSockets, and compiles the post-mortem report.
2. **Log Intelligence Agent:** Ingests microservice, database, and API gateway logs to extract stack traces, warning cascades, and error bursts.
3. **Metrics Agent:** Evaluates telemetry counters (P99/P50 latency, error rates, CPU/RAM utilization, and DB connection pool exhaustion).
4. **Code Intelligence Agent:** Audits recent deployments, Git commits, PR messages, and code diffs to spot unindexed queries, memory allocations, or configuration regressions.
5. **Research Agent:** Investigates architectural failure modes and runbooks with an extensible knowledge provider (Tavily/custom docs).
6. **Root Cause Agent:** Synthesizes the Correlated Evidence Dossier to infer the root cause of the incident.
7. **Response Agent:** Formulates a safe, low-risk remediation strategy constrained exclusively to whitelisted actions.
8. **Recovery Verification Agent:** Audits post-remediation telemetry against nominal baselines to certify recovery.

---

## ⚡ NVIDIA & Nebius Token Factory Integration

IncidentZero uses **Nebius Token Factory** to power real-time reasoning with NVIDIA open-source foundation models:

- **Configured Model:** `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF` (or any Nebius-hosted NVIDIA model).
- **Clean Abstraction:** Core agent logic interfaces with an abstract `AIProvider` base class (`backend/app/ai/provider.py` and `backend/app/ai/nebius.py`).
- **No Hardcoded API Keys & No Fakes:** All credentials load via environment variables. When no key is present, the UI clearly displays **"AI provider not configured"** rather than pretending to work.

---

## 🛡️ AI Safety & Deterministic Sandboxing

IncidentZero strictly isolates **AI reasoning** from **system execution**:
- ❌ **No Arbitrary Code Execution:** The LLM is never allowed to execute raw shell commands, delete files, or alter databases directly.
- ✅ **Strict Action Whitelisting:** Remediations must match permitted actions (`rollback_deployment`, `restart_service`, `restore_previous_configuration`) on authorized target services.
- ✅ **Verification Gate:** The Recovery Agent verifies telemetry recovery before marking the incident resolved.

---

## 🎮 Realistic Production Simulator

Includes 3 simulated failure scenarios across 5 microservices (API Gateway, Payment Service, User Service, Database, Monitoring System):

| Scenario | Injected Failure | Degraded Telemetry | Expected Whitelisted Action |
| :--- | :--- | :--- | :--- |
| **1. Database Query Regression** | PR #1042 introduced an unindexed nested query on audit records table | Latency spikes to ~8.4s, 31% error rate, DB pool hits 100/100 | `rollback_deployment` |
| **2. Memory Leak** | PR #1055 introduced an unbounded in-memory telemetry buffer | Memory reaches 96%, recurring container OOMKilled (code 137) | `restart_service` |
| **3. Dependency Timeout** | Config update disabled circuit breaker and raised fraud timeout to 30s | Worker thread pool starvation, cascaded 504 Gateway Timeouts | `restore_previous_configuration` |

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- Nebius Token Factory API Key (Optional for offline test mode)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-username/incidentzero.git
cd incidentzero

# Copy environment variables
cp .env.example .env
```

Edit `.env` with your Nebius Token Factory credentials:
```ini
NEBIUS_API_KEY=your_nebius_api_key_here
NEBIUS_MODEL=nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
NEBIUS_API_BASE_URL=https://api.tokenfactory.nebius.com/v1
```

### 2. Run Backend
```bash
# Setup virtual environment
python -m venv backend/.venv

# Activate virtual environment
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API is available at `http://localhost:8000` (Swagger UI at `/docs`).

### 3. Run Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🐳 Docker Deployment

Run both backend and frontend with a single command:

```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 🧪 Running the Test Suite

IncidentZero includes unit, simulation, agent contract, and end-to-end integration tests:

```bash
# Run all tests with pytest
backend/.venv/Scripts/python -m pytest backend/tests/ -v
```

All 10 test suites cover:
- FastAPI endpoints & system health
- Microservice simulator & telemetry generation
- Whitelist safety validation
- Multi-agent evidence extraction & database persistence
- Full autonomous investigation pipeline (E2E)

---

## 🎬 Demo Walkthrough

1. Open the **System Operations Dashboard** (`http://localhost:5173`).
2. Click the glowing **"SIMULATE INCIDENT"** button.
3. Select **"Database Query Regression"** and ensure *Auto-Dispatch Multi-Agent Investigation* is checked.
4. Watch the **Interactive Multi-Agent Graph** in real-time as Log, Metrics, Code, and Research agents activate.
5. Inspect the **Telemetry Charts** as P99 latency escalates to 8420ms.
6. Review the **Root Cause Diagnosis** inferred by the Root Cause Agent.
7. Click **"Execute Safe Remediation"** to trigger the whitelisted `rollback_deployment` action.
8. Watch the **Recovery Agent** audit post-remediation metrics and certify recovery.
9. Review and print the authoritative **Post-Mortem Incident Report**.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
