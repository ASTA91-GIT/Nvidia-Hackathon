from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import LogAnalysisResult
from backend.app.ai.prompts import LOG_AGENT_SYSTEM_PROMPT, LOG_AGENT_USER_PROMPT

class LogIntelligenceAgent(BaseAgent[LogAnalysisResult]):
    agent_name = "Log Intelligence Agent"
    agent_role = "Microservice & Server Log Analysis"
    output_schema = LogAnalysisResult

    async def execute(self, input_data: Dict[str, Any]) -> LogAnalysisResult:
        incident_id = input_data.get("incident_id", "unknown")
        service = input_data.get("service", "all")
        logs = input_data.get("logs", [])

        logs_formatted = "\n".join([
            f"[{l.get('timestamp')}] [{l.get('service')}] [{l.get('level')}] {l.get('message')}"
            for l in logs
        ]) if logs else "No active logs found."

        user_prompt = LOG_AGENT_USER_PROMPT.format(
            incident_id=incident_id,
            service=service,
            logs_text=logs_formatted
        )

        return await self.ai_provider.generate_json(
            system_prompt=LOG_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: LogAnalysisResult, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "LOG",
            "title": f"Log Analysis Anomalies ({len(output.anomalies)} detected)",
            "description": output.key_findings,
            "data": {
                "summary": output.summary,
                "anomalies": [a.model_dump() for a in output.anomalies],
                "suspicious_errors": output.suspicious_errors,
                "affected_services": output.affected_services
            }
        }
