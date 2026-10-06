import uuid
import datetime
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.models.database import AgentRun, Evidence
from backend.app.ai.provider import AIProvider, AIProviderNotConfiguredError, AIProviderError

logger = logging.getLogger(__name__)
TOut = TypeVar("TOut", bound=BaseModel)

class AgentExecutionResult(BaseModel, Generic[TOut]):
    agent_name: str
    agent_role: str
    status: str  # COMPLETED, FAILED, UNCONFIGURED
    findings: str
    confidence: float
    output: Optional[TOut] = None
    error_message: Optional[str] = None
    evidence_collected: Optional[Dict[str, Any]] = None

class BaseAgent(ABC, Generic[TOut]):
    agent_name: str
    agent_role: str
    output_schema: Type[TOut]

    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> TOut:
        """Core AI reasoning logic returning structured Pydantic output."""
        pass

    @abstractmethod
    def extract_evidence(self, output: TOut, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured evidence from agent output to save to the investigation dossier."""
        pass

    async def run(
        self,
        db: Session,
        investigation_id: str,
        input_data: Dict[str, Any]
    ) -> AgentExecutionResult[TOut]:
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.utcnow()

        agent_run = AgentRun(
            id=run_id,
            investigation_id=investigation_id,
            agent_name=self.agent_name,
            agent_role=self.agent_role,
            status="RUNNING",
            started_at=now,
            input_payload=input_data
        )
        db.add(agent_run)
        db.commit()

        try:
            # Check AI Provider readiness
            if not self.ai_provider.is_configured():
                raise AIProviderNotConfiguredError(
                    "AI provider not configured. Please set NEBIUS_API_KEY in your environment."
                )

            # Execute Agent Reasoning
            output: TOut = await self.execute(input_data)
            
            # Extract findings & confidence
            findings = getattr(output, "key_findings", getattr(output, "summary", getattr(output, "probable_root_cause", str(output))))
            confidence = getattr(output, "confidence", 1.0)
            output_dict = output.model_dump()

            # Record evidence if any
            evidence_data = self.extract_evidence(output, input_data)
            if evidence_data:
                evidence = Evidence(
                    id=f"evi-{uuid.uuid4().hex[:8]}",
                    investigation_id=investigation_id,
                    source_agent=self.agent_name,
                    evidence_type=evidence_data.get("type", "ANALYSIS"),
                    title=evidence_data.get("title", f"{self.agent_name} Findings"),
                    description=evidence_data.get("description", findings),
                    data=evidence_data.get("data", output_dict),
                    confidence=confidence,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(evidence)

            # Update AgentRun in DB
            agent_run.status = "COMPLETED"
            agent_run.completed_at = datetime.datetime.utcnow()
            agent_run.findings = str(findings)
            agent_run.confidence = float(confidence)
            agent_run.output_payload = output_dict
            db.commit()

            return AgentExecutionResult(
                agent_name=self.agent_name,
                agent_role=self.agent_role,
                status="COMPLETED",
                findings=str(findings),
                confidence=float(confidence),
                output=output,
                evidence_collected=evidence_data
            )

        except AIProviderNotConfiguredError as e:
            err_msg = str(e)
            agent_run.status = "FAILED"
            agent_run.completed_at = datetime.datetime.utcnow()
            agent_run.error_message = err_msg
            agent_run.findings = "Execution paused: AI provider not configured."
            db.commit()
            return AgentExecutionResult(
                agent_name=self.agent_name,
                agent_role=self.agent_role,
                status="FAILED",
                findings="AI provider not configured.",
                confidence=0.0,
                error_message=err_msg
            )
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Agent {self.agent_name} failed: {err_msg}")
            agent_run.status = "FAILED"
            agent_run.completed_at = datetime.datetime.utcnow()
            agent_run.error_message = err_msg
            agent_run.findings = f"Failed to execute: {err_msg}"
            db.commit()
            return AgentExecutionResult(
                agent_name=self.agent_name,
                agent_role=self.agent_role,
                status="FAILED",
                findings=f"Agent error: {err_msg}",
                confidence=0.0,
                error_message=err_msg
            )
