import json
from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import RootCauseDiagnosis
from backend.app.ai.prompts import ROOT_CAUSE_AGENT_SYSTEM_PROMPT, ROOT_CAUSE_AGENT_USER_PROMPT

class RootCauseAgent(BaseAgent[RootCauseDiagnosis]):
    agent_name = "Root Cause Agent"
    agent_role = "Multi-Source Evidence Correlation & Root Cause Diagnosis"
    output_schema = RootCauseDiagnosis

    async def execute(self, input_data: Dict[str, Any]) -> RootCauseDiagnosis:
        incident_id = input_data.get("incident_id", "unknown")
        evidence_dossier = input_data.get("evidence_dossier", [])

        evidence_text = json.dumps(evidence_dossier, indent=2, default=str)

        user_prompt = ROOT_CAUSE_AGENT_USER_PROMPT.format(
            incident_id=incident_id,
            evidence_text=evidence_text
        )

        return await self.ai_provider.generate_json(
            system_prompt=ROOT_CAUSE_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: RootCauseDiagnosis, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "DIAGNOSIS",
            "title": f"Root Cause: {output.diagnosis_title}",
            "description": output.executive_summary,
            "data": {
                "diagnosis_title": output.diagnosis_title,
                "probable_root_cause": output.probable_root_cause,
                "primary_suspect_service": output.primary_suspect_service,
                "contributing_factors": output.contributing_factors,
                "confidence": output.confidence
            }
        }
