import json
import re
import logging
from typing import TypeVar, Type, Optional, Any, Dict
import httpx
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.ai.provider import AIProvider, AIProviderError, AIProviderNotConfiguredError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class NebiusTokenFactoryProvider(AIProvider):
    """
    Nebius Token Factory AI Provider integration.
    Hosts NVIDIA Nemotron and open-source models with OpenAI-compatible endpoints.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0
    ):
        self.api_key = api_key or settings.NEBIUS_API_KEY
        self.model = model or settings.NEBIUS_MODEL
        self.base_url = (base_url or settings.NEBIUS_API_BASE_URL).rstrip("/")
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    def get_model_name(self) -> str:
        return self.model

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown fences and whitespace from JSON response."""
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        return text

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.2
    ) -> T:
        if not self.is_configured():
            raise AIProviderNotConfiguredError(
                "AI provider not configured. Please set NEBIUS_API_KEY in your .env file."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Request schema format guidance in prompt and response_format
        schema_definition = json.dumps(schema_class.model_json_schema(), indent=2)
        augmented_system_prompt = (
            f"{system_prompt}\n\n"
            f"You MUST respond ONLY with valid JSON matching this JSON Schema:\n{schema_definition}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": augmented_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        endpoint = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                if response.status_code == 401:
                    raise AIProviderNotConfiguredError("Nebius API key is invalid or unauthorized.")
                
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                cleaned = self._clean_json_text(content)
                parsed = json.loads(cleaned)
                return schema_class.model_validate(parsed)

        except httpx.HTTPStatusError as e:
            logger.error(f"Nebius API HTTP Error: {e.response.status_code} - {e.response.text}")
            raise AIProviderError(f"Nebius API returned error {e.response.status_code}: {e.response.text}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from model response: {content}")
            raise AIProviderError(f"Model response was not valid JSON: {str(e)}")
        except Exception as e:
            if isinstance(e, AIProviderError):
                raise
            logger.error(f"Error calling Nebius Token Factory: {str(e)}")
            raise AIProviderError(f"AI Provider execution failed: {str(e)}")


class DeterministicTestMockProvider(AIProvider):
    """
    Used EXCLUSIVELY when settings.TEST_MODE=True for automated unit/integration test suites
    to provide deterministic verification without external network dependency.
    """

    def __init__(self, model_name: str = "nvidia/nemotron-test-mock"):
        self.model_name = model_name

    def is_configured(self) -> bool:
        return True

    def get_model_name(self) -> str:
        return self.model_name

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.2
    ) -> T:
        # Dynamically instantiate compliant default instance based on schema
        from backend.app.ai.schemas import (
            LogAnalysisResult, LogAnomaly,
            MetricsAnalysisResult, MetricAnomaly,
            CodeAnalysisResult,
            ResearchResult,
            RootCauseDiagnosis,
            RemediationPlan,
            RecoveryVerificationResult,
            IncidentReportResult
        )

        name = schema_class.__name__

        if name == "LogAnalysisResult":
            return schema_class(
                summary="Log analysis detected severe database pool exhaustion and sequential scan delays.",
                anomalies=[
                    LogAnomaly(
                        service="Database",
                        log_level="ERROR",
                        message_snippet="Max connections reached on primary postgres instance.",
                        frequency_or_impact="100/100 active connections saturated",
                        relevance="Directly causes upstream 504 timeouts"
                    )
                ],
                suspicious_errors=["DBConnectionTimeoutError: Connection pool acquisition timed out after 5000ms."],
                affected_services=["Database", "Payment Service", "API Gateway"],
                confidence=0.96,
                key_findings="Postgres connection starvation caused by slow queries in Payment Service."
            )
        elif name == "MetricsAnalysisResult":
            return schema_class(
                summary="P99 latency spiked over 8000ms with error rate climbing to ~31%.",
                anomalies=[
                    MetricAnomaly(
                        service="Payment Service",
                        metric_name="latency_p99_ms",
                        baseline_value=185.0,
                        incident_value=8420.0,
                        deviation_description="45x spike in P99 latency"
                    )
                ],
                p99_impact="Catastrophic latency escalation to 8420ms",
                error_spike_pct=31.8,
                resource_saturation={"db_pool": "98.5%", "cpu": "89.4%"},
                confidence=0.94,
                key_findings="Resource exhaustion on database pool and Payment Service worker threads."
            )
        elif name == "CodeAnalysisResult":
            return schema_class(
                summary="Commit 7f8a91c added unindexed sequential scan in PaymentLedgerRepository.",
                commit_sha="7f8a91c",
                author="dev-sarah@incidentzero.internal",
                identified_regressions=["Missing compound index on payment_audit_records (customer_id, created_at)"],
                risk_assessment="HIGH",
                is_likely_culprit=True,
                confidence=0.93,
                key_findings="Deployment v2.4.1 directly coincides with the onset of DB latency spikes."
            )
        elif name == "ResearchResult":
            return schema_class(
                query="PostgreSQL sequential scan connection pool exhaustion under OLTP load",
                sources=["PostgreSQL 16 Performance Tuning Guide", "AWS Aurora Connection Pool Patterns"],
                findings="Full table scans on high-traffic tables hold pool connections for multiple seconds, triggering thread starvation.",
                relevance="Matches slow query logs on payment_audit_records table.",
                recommendation="Apply composite indexing and roll back unindexed query deployment."
            )
        elif name == "RootCauseDiagnosis":
            return schema_class(
                diagnosis_title="Unindexed Query Regression in v2.4.1 Causing DB Pool Exhaustion",
                probable_root_cause="Deployment v2.4.1 introduced a slow sequential scan on payment_audit_records. This exhausted all 100 postgres connections, causing cascaded 504 gateway timeouts.",
                primary_suspect_service="Payment Service",
                contributing_factors=["Connection pool max limit reached", "Missing audit table index"],
                supporting_evidence_ids=["log-db-pool-exhaustion", "diff-payment-ledger-repo", "metric-p99-spike"],
                confidence=0.95,
                executive_summary="Payment Service v2.4.1 degraded API throughput by exhausting database connections due to an unindexed query."
            )
        elif name == "RemediationPlan":
            return schema_class(
                action_type="rollback_deployment",
                target_service="Payment Service",
                parameters={"target_version": "v2.4.0"},
                risk_level="LOW",
                expected_recovery_time_seconds=30,
                rationale="Rolling back to v2.4.0 eliminates the unindexed query and immediately drains connection contention.",
                rollback_plan="Restart payment service pods if lingering connections persist."
            )
        elif name == "RecoveryVerificationResult":
            return schema_class(
                is_recovered=True,
                latency_delta_ms=8228.0,
                error_rate_delta_pct=31.3,
                status_assessment="P99 latency returned to 192ms (nominal). Error rate dropped to 0.5%.",
                remaining_risks=[],
                verification_passed=True
            )
        elif name == "IncidentReportResult":
            return schema_class(
                title="Post-Mortem: Payment API Latency Degradation",
                executive_summary="SEV1 incident resolved autonomously via multi-agent correlation and safe rollback.",
                impact_assessment="31% of checkout transactions degraded between 10:15 and 10:28 UTC.",
                root_cause_analysis="Full table scan on audit ledger introduced in PR #1042 saturated the PostgreSQL connection pool.",
                remediation_details="Executed safe deployment rollback to v2.4.0.",
                lessons_learned=["Enforce EXPLAIN ANALYZE checks in CI pipeline", "Add circuit breaker to audit queries"],
                preventative_measures=["Add migration index on payment_audit_records", "Tune pool timeout threshold"]
            )
        
        # Fallback to model instantiation
        return schema_class.model_construct()


def get_ai_provider() -> AIProvider:
    """Provider factory respecting configuration and test mode."""
    if settings.TEST_MODE:
        return DeterministicTestMockProvider()
    return NebiusTokenFactoryProvider()
