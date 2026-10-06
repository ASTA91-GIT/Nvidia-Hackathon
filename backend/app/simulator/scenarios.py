import datetime
from typing import Dict, Any, List

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "scenario_db_regression": {
        "id": "scenario_db_regression",
        "title": "Payment API Latency Spike & DB Connection Pool Exhaustion",
        "description": "Payment Gateway response time degraded severely following v2.4.1 release. High error rate on /v1/charges.",
        "service": "Payment Service",
        "severity": "SEV1",
        "expected_action": "rollback_deployment",
        "expected_target_service": "Payment Service",
        "baseline_metrics": {
            "latency_p99_ms": 185.0,
            "latency_p50_ms": 42.0,
            "error_rate_pct": 0.4,
            "cpu_usage_pct": 28.5,
            "memory_usage_pct": 45.2,
            "db_pool_utilization_pct": 18.0
        },
        "incident_metrics": {
            "latency_p99_ms": 8420.0,
            "latency_p50_ms": 6120.0,
            "error_rate_pct": 31.8,
            "cpu_usage_pct": 89.4,
            "memory_usage_pct": 68.1,
            "db_pool_utilization_pct": 98.5
        },
        "recovery_metrics": {
            "latency_p99_ms": 192.0,
            "latency_p50_ms": 44.0,
            "error_rate_pct": 0.5,
            "cpu_usage_pct": 29.8,
            "memory_usage_pct": 46.0,
            "db_pool_utilization_pct": 21.0
        },
        "deployment": {
            "service": "Payment Service",
            "version": "v2.4.1",
            "commit_sha": "7f8a91c",
            "commit_message": "feat(payments): batch audit ledger query with customer history join (#1042)",
            "author": "dev-sarah@incidentzero.internal",
            "diff_summary": "Added query in PaymentLedgerRepository to fetch historical audit transactions on every charge verification without compound index on (customer_id, created_at).",
            "code_diff": """@@ -42,6 +42,12 @@ class PaymentLedgerRepository:
     async def verify_and_record(self, tx: Transaction) -> bool:
+        # New audit check added in v2.4.1
+        # WARNING: full table scan on audit_records table without index on tenant_id
+        query = \"\"\"
+            SELECT a.* FROM payment_audit_records a
+            WHERE a.customer_id = :cid AND a.status = 'SETTLED'
+            ORDER BY a.created_at DESC
+        \"\"\"
+        records = await self.db.execute_raw(query, cid=tx.customer_id)
         return await self._process_gateway_charge(tx)"""
        },
        "logs": [
            {
                "service": "API Gateway",
                "level": "INFO",
                "message": "Routing POST /v1/charges to Payment Service upstream pod payment-svc-784f9"
            },
            {
                "service": "Payment Service",
                "level": "INFO",
                "message": "Payment Service version v2.4.1 initialized. Deployment 7f8a91c active."
            },
            {
                "service": "Database",
                "level": "WARN",
                "message": "PostgreSQL slow query detected: SELECT a.* FROM payment_audit_records a WHERE a.customer_id = $1 (execution time: 5412ms, Seq Scan on payment_audit_records)"
            },
            {
                "service": "Payment Service",
                "level": "ERROR",
                "message": "DBConnectionTimeoutError: Connection pool acquisition timed out after 5000ms. Active: 100/100 connections held."
            },
            {
                "service": "API Gateway",
                "level": "ERROR",
                "message": "HTTP 504 Gateway Timeout on upstream payment-svc-784f9 for request /v1/charges (client IP: 198.51.100.24)"
            },
            {
                "service": "Monitoring System",
                "level": "WARN",
                "message": "Alert triggered: P99 latency breach (>5000ms threshold) on service payment-service"
            },
            {
                "service": "Database",
                "level": "ERROR",
                "message": "Max connections reached on primary postgres instance. 100 active connections in state 'idle in transaction / executing slow scan'."
            }
        ],
        "probable_root_cause_summary": "Deployment v2.4.1 (commit 7f8a91c) introduced an unindexed sequential scan in PaymentLedgerRepository on payment_audit_records, exhausting the PostgreSQL connection pool (100/100) and causing HTTP 504 timeouts across the API Gateway.",
        "recommended_remediation": "rollback_deployment",
        "remediation_rationale": "Roll back Payment Service deployment to previous stable release v2.4.0 (commit e12b304) to immediately release database connection locks and restore sub-200ms latency."
    },
    
    "scenario_memory_leak": {
        "id": "scenario_memory_leak",
        "title": "Payment Service Pod OOM Crashes & Memory Saturation",
        "description": "Continuous memory growth and repeated container restarts (OOMKilled) on Payment Service worker instances.",
        "service": "Payment Service",
        "severity": "SEV1",
        "expected_action": "restart_service",
        "expected_target_service": "Payment Service",
        "baseline_metrics": {
            "latency_p99_ms": 210.0,
            "latency_p50_ms": 48.0,
            "error_rate_pct": 0.2,
            "cpu_usage_pct": 32.0,
            "memory_usage_pct": 42.0,
            "db_pool_utilization_pct": 22.0
        },
        "incident_metrics": {
            "latency_p99_ms": 4890.0,
            "latency_p50_ms": 2800.0,
            "error_rate_pct": 24.5,
            "cpu_usage_pct": 96.0,
            "memory_usage_pct": 95.8,
            "db_pool_utilization_pct": 45.0
        },
        "recovery_metrics": {
            "latency_p99_ms": 220.0,
            "latency_p50_ms": 50.0,
            "error_rate_pct": 0.3,
            "cpu_usage_pct": 33.5,
            "memory_usage_pct": 44.0,
            "db_pool_utilization_pct": 23.0
        },
        "deployment": {
            "service": "Payment Service",
            "version": "v2.4.0-patch1",
            "commit_sha": "9b1c43d",
            "commit_message": "fix(events): append telemetry payloads into global batch buffer (#1055)",
            "author": "dev-alex@incidentzero.internal",
            "diff_summary": "Telemetry worker appends raw request/response objects to unconstrained global list memory buffer without periodic flush or max heap ceiling.",
            "code_diff": """@@ -15,5 +15,9 @@ class TelemetryBatchCollector:
     def __init__(self):
-        self.buffer = collections.deque(maxlen=1000)
+        # Removed fixed size deque to prevent telemetry event drops
+        self.buffer = []  # Unbounded memory growth on high transaction volume
+
     def record_event(self, event_data: dict):
+        self.buffer.append(event_data)"""
        },
        "logs": [
            {
                "service": "Payment Service",
                "level": "WARN",
                "message": "Memory warning: JVM/V8 Heap usage at 88% (3.52 GB of 4.0 GB limit). Garbage collection pause: 840ms."
            },
            {
                "service": "Payment Service",
                "level": "ERROR",
                "message": "Fatal error: Out of Memory (OOM). Container terminated with exit code 137 (SIGKILL)."
            },
            {
                "service": "API Gateway",
                "level": "ERROR",
                "message": "502 Bad Gateway: Upstream connection refused to payment-svc-worker (pod crashing)."
            },
            {
                "service": "Monitoring System",
                "level": "WARN",
                "message": "Kubernetes Pod CrashLoopBackOff: payment-service-worker-6b98 restart count: 6."
            },
            {
                "service": "User Service",
                "level": "WARN",
                "message": "Failed to sync user transaction history with Payment Service: connection reset by peer."
            }
        ],
        "probable_root_cause_summary": "Telemetry collector was updated with an unbounded in-memory buffer, causing rapid memory saturation (95%+ RAM usage) and recurring OOM container terminations (exit code 137).",
        "recommended_remediation": "restart_service",
        "remediation_rationale": "Perform graceful rolling restart of payment service pods to purge bloated memory heap and mitigate immediate outage while patch #1056 is prepared."
    },

    "scenario_dependency_failure": {
        "id": "scenario_dependency_failure",
        "title": "Third-Party Fraud Gateway Timeout & Missing Circuit Breaker",
        "description": "Downstream partner API degradation causing thread pool exhaustion in Payment Service due to unconfigured timeout threshold.",
        "service": "Payment Service",
        "severity": "SEV2",
        "expected_action": "restore_previous_configuration",
        "expected_target_service": "Payment Service",
        "baseline_metrics": {
            "latency_p99_ms": 195.0,
            "latency_p50_ms": 45.0,
            "error_rate_pct": 0.3,
            "cpu_usage_pct": 25.0,
            "memory_usage_pct": 40.0,
            "db_pool_utilization_pct": 15.0
        },
        "incident_metrics": {
            "latency_p99_ms": 7200.0,
            "latency_p50_ms": 5500.0,
            "error_rate_pct": 28.0,
            "cpu_usage_pct": 74.0,
            "memory_usage_pct": 52.0,
            "db_pool_utilization_pct": 30.0
        },
        "recovery_metrics": {
            "latency_p99_ms": 205.0,
            "latency_p50_ms": 47.0,
            "error_rate_pct": 0.4,
            "cpu_usage_pct": 27.0,
            "memory_usage_pct": 41.0,
            "db_pool_utilization_pct": 16.0
        },
        "deployment": {
            "service": "Payment Service",
            "version": "config-update-38",
            "commit_sha": "3a4f890",
            "commit_message": "chore(config): adjust fraud evaluation timeout and disable circuit breaker bypass (#1062)",
            "author": "dev-ops@incidentzero.internal",
            "diff_summary": "Configuration change increased fraud provider HTTP timeout from 500ms to 30000ms and disabled fallback circuit breaker.",
            "code_diff": """@@ -8,4 +8,4 @@
-FRAUD_GATEWAY_TIMEOUT_MS=500
-CIRCUIT_BREAKER_ENABLED=true
+FRAUD_GATEWAY_TIMEOUT_MS=30000
+CIRCUIT_BREAKER_ENABLED=false"""
        },
        "logs": [
            {
                "service": "Payment Service",
                "level": "INFO",
                "message": "Applying config update config-update-38: fraud timeout set to 30000ms, circuit breaker disabled."
            },
            {
                "service": "Payment Service",
                "level": "WARN",
                "message": "External fraud gateway https://fraud-api.partner.io taking >12000ms to respond for customer risk scoring."
            },
            {
                "service": "Payment Service",
                "level": "ERROR",
                "message": "Worker thread pool starvation: all 128 worker threads blocked waiting for external HTTP fraud response."
            },
            {
                "service": "API Gateway",
                "level": "ERROR",
                "message": "504 Gateway Timeout: payment-service failed to respond within 10s timeout threshold."
            },
            {
                "service": "Monitoring System",
                "level": "WARN",
                "message": "High error rate alarm: Payment Service 5xx responses exceeded 25%."
            }
        ],
        "probable_root_cause_summary": "Configuration update disabled the circuit breaker and set fraud gateway timeout to 30s. When the external provider slowed down, all payment worker threads were blocked.",
        "recommended_remediation": "restore_previous_configuration",
        "remediation_rationale": "Restore previous configuration with 500ms timeout and circuit breaker enabled to allow immediate fallback to async evaluation."
    }
}
