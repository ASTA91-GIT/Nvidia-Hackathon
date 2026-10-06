import json
from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import RecoveryVerificationResult
from backend.app.ai.prompts import RECOVERY_AGENT_SYSTEM_PROMPT, RECOVERY_AGENT_USER_PROMPT

class RecoveryVerificationAgent(BaseAgent[RecoveryVerificationResult]):
    agent_name = "Recovery Verification Agent"
    agent_role = "Post-Remediation Health Audit & Recovery Certification"
    output_schema = RecoveryVerificationResult

    async def execute(self, input_data: Dict[str, Any]) -> RecoveryVerificationResult:
        base_m = json.dumps(input_data.get("baseline_metrics", {}), indent=2)
        inc_m = json.dumps(input_data.get("incident_metrics", {}), indent=2)
        rec_m = json.dumps(input_data.get("post_remediation_metrics", {}), indent=2)

        user_prompt = RECOVERY_AGENT_USER_PROMPT.format(
            baseline_metrics=base_m,
            incident_metrics=inc_m,
            post_remediation_metrics=rec_m
        )

        return await self.ai_provider.generate_json(
            system_prompt=RECOVERY_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: RecoveryVerificationResult, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "RECOVERY",
            "title": f"Health Audit: {'RECOVERY CERTIFIED' if output.is_recovered else 'RECOVERY FAILED'}",
            "description": output.status_assessment,
            "data": {
                "is_recovered": output.is_recovered,
                "latency_delta_ms": output.latency_delta_ms,
                "error_rate_delta_pct": output.error_rate_delta_pct,
                "verification_passed": output.verification_passed,
                "remaining_risks": output.remaining_risks
            }
        }
