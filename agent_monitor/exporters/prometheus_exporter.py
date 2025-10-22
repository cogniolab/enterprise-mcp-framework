"""
Prometheus Exporter for Agent Monitor

Export agent metrics to Prometheus for monitoring and alerting.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server


@dataclass
class PrometheusConfig:
    """
    Configuration for Prometheus exporter.

    Args:
        port: Port to expose metrics endpoint (default: 9090)
        prefix: Metric name prefix (default: "agent_monitor")
    """
    port: int = 9090
    prefix: str = "agent_monitor"


class PrometheusExporter:
    """
    Export Agent Monitor metrics to Prometheus.

    Exposes metrics at http://localhost:{port}/metrics

    Example:
        >>> exporter = PrometheusExporter(PrometheusConfig(port=9090))
        >>> exporter.start()
        >>> exporter.record_request("customer_support", 2.3, 0.05, True)
    """

    def __init__(self, config: PrometheusConfig):
        """Initialize Prometheus exporter."""
        self.config = config
        self._create_metrics()

    def _create_metrics(self):
        """Create Prometheus metrics."""
        prefix = self.config.prefix

        # Request metrics
        self.requests_total = Counter(
            f"{prefix}_requests_total",
            "Total number of agent requests",
            ["agent", "operation", "status"],
        )

        self.requests_duration = Histogram(
            f"{prefix}_requests_duration_seconds",
            "Agent request duration",
            ["agent", "operation"],
        )

        # Cost metrics
        self.cost_total = Counter(
            f"{prefix}_cost_total_usd",
            "Total cost in USD",
            ["agent", "operation"],
        )

        # Token metrics
        self.tokens_input = Counter(
            f"{prefix}_tokens_input_total",
            "Input tokens consumed",
            ["agent", "model"],
        )

        self.tokens_output = Counter(
            f"{prefix}_tokens_output_total",
            "Output tokens generated",
            ["agent", "model"],
        )

    def start(self):
        """Start the Prometheus metrics server."""
        start_http_server(self.config.port)

    def record_request(
        self,
        agent_name: str,
        duration: float,
        cost: float,
        success: bool,
        operation: str = "default",
    ):
        """Record a request metric."""
        status = "success" if success else "error"
        self.requests_total.labels(agent=agent_name, operation=operation, status=status).inc()
        self.requests_duration.labels(agent=agent_name, operation=operation).observe(duration)
        self.cost_total.labels(agent=agent_name, operation=operation).inc(cost)
