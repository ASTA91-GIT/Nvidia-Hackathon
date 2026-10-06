import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
from backend.app.config import settings
from backend.app.agents.base import BaseAgent
from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import ResearchResult
from backend.app.ai.prompts import RESEARCH_AGENT_SYSTEM_PROMPT, RESEARCH_AGENT_USER_PROMPT

logger = logging.getLogger(__name__)

class ResearchProvider(ABC):
    @abstractmethod
    async def query_knowledge(self, query: str) -> List[Dict[str, str]]:
        pass

class TavilyResearchProvider(ResearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY

    async def query_knowledge(self, query: str) -> List[Dict[str, str]]:
        if not self.api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.api_key, "query": query, "search_depth": "basic"}
                )
                if res.status_code == 200:
                    data = res.json()
                    return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")} for r in data.get("results", [])]
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
        return []

class ResearchAgent(BaseAgent[ResearchResult]):
    agent_name = "Research Agent"
    agent_role = "Technical Documentation & Failure Pattern Research"
    output_schema = ResearchResult

    def __init__(self, ai_provider: AIProvider, research_provider: Optional[ResearchProvider] = None):
        super().__init__(ai_provider)
        self.research_provider = research_provider or TavilyResearchProvider()

    async def execute(self, input_data: Dict[str, Any]) -> ResearchResult:
        incident_id = input_data.get("incident_id", "unknown")
        symptoms = input_data.get("symptoms", "High latency and connection timeouts")
        errors = input_data.get("errors", "Pool timeout / out of memory / gateway 504")

        # Query external research provider if configured
        query_text = f"{symptoms} {errors}"
        external_context = await self.research_provider.query_knowledge(query_text)
        
        external_notes = ""
        if external_context:
            external_notes = "\nExternal SRE Research Snippets:\n" + "\n".join([
                f"- {item.get('title')}: {item.get('snippet')}" for item in external_context[:3]
            ])

        user_prompt = RESEARCH_AGENT_USER_PROMPT.format(
            incident_id=incident_id,
            symptoms=symptoms + external_notes,
            errors=errors
        )

        return await self.ai_provider.generate_json(
            system_prompt=RESEARCH_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_class=self.output_schema
        )

    def extract_evidence(self, output: ResearchResult, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {
            "type": "DOC",
            "title": f"Technical Research: {output.query}",
            "description": output.findings,
            "data": {
                "query": output.query,
                "sources": output.sources,
                "findings": output.findings,
                "relevance": output.relevance,
                "recommendation": output.recommendation
            }
        }
