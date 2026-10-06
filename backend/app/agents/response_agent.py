import json
from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import RemediationPlan
from backend.app.ai.prompts import RESPONSE_AGENT_SYSTEM_PROMPT, RESPONSE_AGENT_USER_PROMPT
from backend.app.simulator.remediation import ALLOWED_REMEDIATION_ACTIONS

class ResponseAgent(BaseAgent[RemediationPlan]):
    agent_name = "Response Agent"
    agent_role = "Safe Remediation Strategy & Action Formulation"
    output_schema = RemediationPlan

    async def execute(self, input_data: Dict[str, Any]) -> RemediationPlan:
        service = input_data.get("service", "Payment Service")
        diagnosis = input_data.get("diagnosis", {})

        diagnosis_text = json.dumps(diagnosis, indent=2, default=str)

        user_prompt = RESPONSE_AGENT_USER_PROMPT.format(
            diagnosis_text=diagnosis_text,
            service=service
        )

        plan = await self.ai_provider.generate_json(
            system_prompt=RESPONSE_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

        # AI Safety verification layer: Ensure recommended action is in explicit whitelist
        if plan.action_type not in ALLOWED_REMEDIATION_ACTIONS:
            plan.action_type = "rollback_deployment"  # Fallback to safest default allowed action
            plan.risk_level = "LOW"

        return plan

    def extract_evidence(self, output: RemediationPlan, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "RESPONSE_PLAN",
            "title": f"Remediation Proposal: {output.action_type}",
            "description": output.rationale,
            "data": {
                "action_type": output.action_type,
                "target_service": output.target_service,
                "risk_level": output.risk_level,
                "expected_recovery_time_seconds": output.expected_recovery_time_seconds,
                "rollback_plan": output.rollback_plan
            }
        }
