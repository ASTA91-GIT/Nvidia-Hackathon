from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.ai.schemas import CodeAnalysisResult
from backend.app.ai.prompts import CODE_AGENT_SYSTEM_PROMPT, CODE_AGENT_USER_PROMPT

class CodeIntelligenceAgent(BaseAgent[CodeAnalysisResult]):
    agent_name = "Code Intelligence Agent"
    agent_role = "Git Commits, Releases, and Diff Inspection"
    output_schema = CodeAnalysisResult

    async def execute(self, input_data: Dict[str, Any]) -> CodeAnalysisResult:
        incident_id = input_data.get("incident_id", "unknown")
        deployment = input_data.get("deployment") or {}

        dep_text = (
            f"Service: {deployment.get('service')}\n"
            f"Version: {deployment.get('version')}\n"
            f"Commit: {deployment.get('commit_sha')}\n"
            f"Author: {deployment.get('author')}\n"
            f"Message: {deployment.get('commit_message')}\n"
            f"Diff Summary: {deployment.get('diff_summary')}\n"
            f"CODE DIFF:\n{deployment.get('code_diff')}\n"
        ) if deployment else "No recent deployments recorded in this window."

        user_prompt = CODE_AGENT_USER_PROMPT.format(
            incident_id=incident_id,
            commit_sha=deployment.get("commit_sha", "unknown"),
            author=deployment.get("author", "unknown"),
            deployment_text=dep_text
        )

        return await self.ai_provider.generate_json(
            system_prompt=CODE_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: CodeAnalysisResult, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "CODE_DIFF",
            "title": f"Code Regression Analysis (Commit {output.commit_sha})",
            "description": output.key_findings,
            "data": {
                "summary": output.summary,
                "commit_sha": output.commit_sha,
                "identified_regressions": output.identified_regressions,
                "risk_assessment": output.risk_assessment,
                "is_likely_culprit": output.is_likely_culprit
            }
        }
