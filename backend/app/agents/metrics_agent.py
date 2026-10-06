import json
from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import MetricsAnalysisResult
from backend.app.ai.prompts import METRICS_AGENT_SYSTEM_PROMPT, METRICS_AGENT_USER_PROMPT

class MetricsAgent(BaseAgent[MetricsAnalysisResult]):
    agent_name = "Metrics Agent"
    agent_role = "Telemetry, Latency, and Saturation Analysis"
    output_schema = MetricsAnalysisResult

    async def execute(self, input_data: Dict[str, Any]) -> MetricsAnalysisResult:
        incident_id = input_data.get("incident_id", "unknown")
        metrics = input_data.get("metrics", [])

        metrics_text = json.dumps(metrics, indent=2, default=str)

        user_prompt = METRICS_AGENT_USER_PROMPT.format(
            incident_id=incident_id,
            metrics_text=metrics_text
        )

        return await self.ai_provider.generate_json(
            system_prompt=METRICS_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: MetricsAnalysisResult, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "METRIC",
            "title": f"Telemetry Degradation Evidence (P99: {output.p99_impact})",
            "description": output.key_findings,
            "data": {
                "summary": output.summary,
                "anomalies": [a.model_dump() for a in output.anomalies],
                "error_spike_pct": output.error_spike_pct,
                "resource_saturation": output.resource_saturation
            }
        }
