"""
OpenTelemetry Exporter for Agent Monitor

Export agent telemetry data to OpenTelemetry-compatible backends like:
- Jaeger (distributed tracing)
- Datadog (APM and metrics)
- New Relic (full-stack observability)
- Prometheus (metrics)
- Grafana Cloud (dashboards)
- AWS X-Ray (AWS-native tracing)
- Google Cloud Trace (GCP-native tracing)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("Warning: OpenTelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")


@dataclass
class OpenTelemetryConfig:
    """
    Configuration for OpenTelemetry exporter.

    Args:
        service_name: Name of the service (e.g., "agent-monitor")
        endpoint: OTLP endpoint (e.g., "http://localhost:4317")
        backend: Backend type ("jaeger", "datadog", "newrelic", "otlp")
        headers: Authentication headers (e.g., API keys)
        export_interval_ms: Metrics export interval in milliseconds
        enable_traces: Enable distributed tracing
        enable_metrics: Enable metrics export
        enable_logs: Enable log export
        resource_attributes: Additional resource attributes
    """
    service_name: str = "agent-monitor"
    endpoint: str = "http://localhost:4317"
    backend: str = "otlp"  # otlp, jaeger, datadog, newrelic
    headers: Dict[str, str] = field(default_factory=dict)
    export_interval_ms: int = 30000  # 30 seconds
    enable_traces: bool = True
    enable_metrics: bool = True
    enable_logs: bool = False
    resource_attributes: Dict[str, str] = field(default_factory=dict)

    # Backend-specific settings
    datadog_site: str = "datadoghq.com"  # or datadoghq.eu
    newrelic_api_key: Optional[str] = None
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831


class OpenTelemetryExporter:
    """
    Export Agent Monitor telemetry to OpenTelemetry backends.

    Supports multiple backends:
    - **Jaeger**: Open-source distributed tracing
    - **Datadog**: Commercial APM and monitoring
    - **New Relic**: Full-stack observability
    - **OTLP**: OpenTelemetry Protocol (generic)
    - **Prometheus**: Metrics (via OTLP)
    - **Grafana Cloud**: Dashboards and alerts

    Example:
        >>> config = OpenTelemetryConfig(
        ...     service_name="my-agent",
        ...     backend="datadog",
        ...     headers={"DD-API-KEY": "your_api_key"}
        ... )
        >>> exporter = OpenTelemetryExporter(config)
        >>> exporter.start()
        >>>
        >>> # Export a trace
        >>> with exporter.trace_operation("agent_execution") as span:
        ...     span.set_attribute("agent.name", "customer_support")
        ...     span.set_attribute("agent.cost_usd", 0.05)
        ...     # Your agent code here
        >>>
        >>> # Export metrics
        >>> exporter.record_metric("agent.requests.total", 1, {"agent": "customer_support"})
        >>> exporter.record_metric("agent.cost.total_usd", 0.05, {"agent": "customer_support"})
    """

    def __init__(self, config: OpenTelemetryConfig):
        """Initialize OpenTelemetry exporter."""
        if not OTEL_AVAILABLE:
            raise ImportError(
                "OpenTelemetry is not installed. "
                "Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp"
            )

        self.config = config
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None
        self._metrics: Dict[str, Any] = {}

    def start(self):
        """Start the OpenTelemetry exporter."""
        # Create resource attributes
        resource_attrs = {
            "service.name": self.config.service_name,
            "service.version": "1.0.0",
            "deployment.environment": "production",
        }
        resource_attrs.update(self.config.resource_attributes)
        resource = Resource(attributes=resource_attrs)

        # Setup tracing
        if self.config.enable_traces:
            self._setup_tracing(resource)

        # Setup metrics
        if self.config.enable_metrics:
            self._setup_metrics(resource)

    def _setup_tracing(self, resource: Resource):
        """Setup distributed tracing."""
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)

        # Create span exporter based on backend
        if self.config.backend == "jaeger":
            span_exporter = JaegerExporter(
                agent_host_name=self.config.jaeger_agent_host,
                agent_port=self.config.jaeger_agent_port,
            )
        elif self.config.backend == "datadog":
            # Datadog uses OTLP endpoint
            endpoint = f"https://trace.agent.{self.config.datadog_site}:4317"
            span_exporter = OTLPSpanExporter(
                endpoint=endpoint,
                headers=self.config.headers,
            )
        elif self.config.backend == "newrelic":
            # New Relic uses OTLP endpoint
            span_exporter = OTLPSpanExporter(
                endpoint="https://otlp.nr-data.net:4317",
                headers={
                    "api-key": self.config.newrelic_api_key or "",
                    **self.config.headers
                },
            )
        else:  # otlp
            span_exporter = OTLPSpanExporter(
                endpoint=self.config.endpoint,
                headers=self.config.headers,
            )

        # Add span processor
        span_processor = BatchSpanProcessor(span_exporter)
        self.tracer_provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)

    def _setup_metrics(self, resource: Resource):
        """Setup metrics export."""
        # Create metric exporter based on backend
        if self.config.backend == "datadog":
            endpoint = f"https://api.{self.config.datadog_site}:4317"
            metric_exporter = OTLPMetricExporter(
                endpoint=endpoint,
                headers=self.config.headers,
            )
        elif self.config.backend == "newrelic":
            metric_exporter = OTLPMetricExporter(
                endpoint="https://otlp.nr-data.net:4317",
                headers={
                    "api-key": self.config.newrelic_api_key or "",
                    **self.config.headers
                },
            )
        else:  # otlp or jaeger (metrics via OTLP)
            metric_exporter = OTLPMetricExporter(
                endpoint=self.config.endpoint,
                headers=self.config.headers,
            )

        # Create metric reader
        metric_reader = PeriodicExportingMetricReader(
            metric_exporter,
            export_interval_millis=self.config.export_interval_ms,
        )

        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )

        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(__name__)

        # Create common metrics
        self._create_metrics()

    def _create_metrics(self):
        """Create commonly used metrics."""
        if not self.meter:
            return

        # Request metrics
        self._metrics["requests_total"] = self.meter.create_counter(
            name="agent.requests.total",
            description="Total number of agent requests",
            unit="1",
        )

        self._metrics["requests_duration"] = self.meter.create_histogram(
            name="agent.requests.duration",
            description="Agent request duration",
            unit="s",
        )

        self._metrics["requests_errors"] = self.meter.create_counter(
            name="agent.requests.errors",
            description="Total number of agent errors",
            unit="1",
        )

        # Cost metrics
        self._metrics["cost_total_usd"] = self.meter.create_counter(
            name="agent.cost.total_usd",
            description="Total cost in USD",
            unit="USD",
        )

        self._metrics["cost_per_request"] = self.meter.create_histogram(
            name="agent.cost.per_request",
            description="Cost per request in USD",
            unit="USD",
        )

        # Token metrics
        self._metrics["tokens_input"] = self.meter.create_counter(
            name="agent.tokens.input",
            description="Input tokens consumed",
            unit="1",
        )

        self._metrics["tokens_output"] = self.meter.create_counter(
            name="agent.tokens.output",
            description="Output tokens generated",
            unit="1",
        )

        # Tool usage metrics
        self._metrics["tools_calls"] = self.meter.create_counter(
            name="agent.tools.calls",
            description="Tool invocations",
            unit="1",
        )

    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Create a trace span for an operation.

        Args:
            operation_name: Name of the operation (e.g., "agent_execution")
            attributes: Span attributes (e.g., {"agent.name": "customer_support"})

        Returns:
            Span context manager

        Example:
            >>> with exporter.trace_operation("agent_execution", {"agent.name": "support"}) as span:
            ...     # Your code here
            ...     span.set_attribute("agent.cost_usd", 0.05)
        """
        if not self.tracer:
            raise RuntimeError("Tracing not enabled. Set enable_traces=True in config.")

        span = self.tracer.start_span(operation_name)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        return span

    def record_metric(self, metric_name: str, value: float, attributes: Optional[Dict[str, str]] = None):
        """
        Record a metric value.

        Args:
            metric_name: Name of the metric (e.g., "agent.requests.total")
            value: Metric value
            attributes: Metric attributes (e.g., {"agent": "customer_support"})

        Example:
            >>> exporter.record_metric("agent.requests.total", 1, {"agent": "support"})
            >>> exporter.record_metric("agent.cost.total_usd", 0.05, {"agent": "support"})
        """
        attrs = attributes or {}

        # Extract metric type from name
        if "total" in metric_name or "count" in metric_name or "calls" in metric_name:
            # Counter metric
            metric_key = metric_name.replace("agent.", "").replace(".", "_")
            if metric_key in self._metrics:
                self._metrics[metric_key].add(value, attributes=attrs)
        elif "duration" in metric_name or "latency" in metric_name or "per_request" in metric_name:
            # Histogram metric
            metric_key = metric_name.replace("agent.", "").replace(".", "_")
            if metric_key in self._metrics:
                self._metrics[metric_key].record(value, attributes=attrs)

    def export_agent_execution(
        self,
        agent_name: str,
        operation: str,
        duration_seconds: float,
        cost_usd: float,
        tokens_input: int,
        tokens_output: int,
        success: bool,
        error: Optional[str] = None,
        tool_calls: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Export complete agent execution telemetry.

        This is a convenience method that exports both traces and metrics
        for a complete agent execution.

        Args:
            agent_name: Name of the agent
            operation: Operation performed (e.g., "chat_completion")
            duration_seconds: Execution duration in seconds
            cost_usd: Cost in USD
            tokens_input: Input tokens consumed
            tokens_output: Output tokens generated
            success: Whether execution succeeded
            error: Error message if failed
            tool_calls: List of tool names called
            metadata: Additional metadata

        Example:
            >>> exporter.export_agent_execution(
            ...     agent_name="customer_support",
            ...     operation="chat_completion",
            ...     duration_seconds=2.3,
            ...     cost_usd=0.05,
            ...     tokens_input=1500,
            ...     tokens_output=500,
            ...     success=True,
            ...     tool_calls=["search_docs", "create_ticket"],
            ... )
        """
        attrs = {
            "agent.name": agent_name,
            "agent.operation": operation,
        }

        if metadata:
            for key, value in metadata.items():
                attrs[f"agent.metadata.{key}"] = str(value)

        # Create trace span
        if self.tracer:
            with self.tracer.start_as_current_span(f"agent.{operation}") as span:
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.operation", operation)
                span.set_attribute("agent.duration_seconds", duration_seconds)
                span.set_attribute("agent.cost_usd", cost_usd)
                span.set_attribute("agent.tokens.input", tokens_input)
                span.set_attribute("agent.tokens.output", tokens_output)
                span.set_attribute("agent.success", success)

                if error:
                    span.set_status(Status(StatusCode.ERROR, error))
                    span.set_attribute("agent.error", error)
                else:
                    span.set_status(Status(StatusCode.OK))

                if tool_calls:
                    span.set_attribute("agent.tools", json.dumps(tool_calls))
                    span.set_attribute("agent.tools.count", len(tool_calls))

        # Record metrics
        str_attrs = {k: str(v) for k, v in attrs.items()}

        self.record_metric("agent.requests.total", 1, str_attrs)
        self.record_metric("agent.requests.duration", duration_seconds, str_attrs)
        self.record_metric("agent.cost.total_usd", cost_usd, str_attrs)
        self.record_metric("agent.cost.per_request", cost_usd, str_attrs)
        self.record_metric("agent.tokens.input", tokens_input, str_attrs)
        self.record_metric("agent.tokens.output", tokens_output, str_attrs)

        if not success:
            self.record_metric("agent.requests.errors", 1, str_attrs)

        if tool_calls:
            self.record_metric("agent.tools.calls", len(tool_calls), str_attrs)

    def shutdown(self):
        """Shutdown the exporter and flush all pending telemetry."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()

        if self.meter_provider:
            self.meter_provider.shutdown()


# Preset configurations for popular backends

def create_jaeger_config(
    service_name: str = "agent-monitor",
    agent_host: str = "localhost",
    agent_port: int = 6831,
) -> OpenTelemetryConfig:
    """
    Create config for Jaeger backend.

    Jaeger is an open-source distributed tracing platform.

    Setup:
        docker run -d --name jaeger \\
          -p 6831:6831/udp \\
          -p 16686:16686 \\
          jaegertracing/all-in-one:latest

    View traces: http://localhost:16686

    Example:
        >>> config = create_jaeger_config(service_name="my-agent")
        >>> exporter = OpenTelemetryExporter(config)
        >>> exporter.start()
    """
    return OpenTelemetryConfig(
        service_name=service_name,
        backend="jaeger",
        jaeger_agent_host=agent_host,
        jaeger_agent_port=agent_port,
        enable_traces=True,
        enable_metrics=False,  # Jaeger is traces-only
    )


def create_datadog_config(
    service_name: str = "agent-monitor",
    api_key: str = "",
    site: str = "datadoghq.com",
) -> OpenTelemetryConfig:
    """
    Create config for Datadog backend.

    Datadog is a commercial APM and monitoring platform.

    Setup:
        1. Get API key from https://app.datadoghq.com/organization-settings/api-keys
        2. Set DD_API_KEY environment variable

    View data: https://app.datadoghq.com/apm/traces

    Example:
        >>> import os
        >>> config = create_datadog_config(
        ...     service_name="my-agent",
        ...     api_key=os.getenv("DD_API_KEY"),
        ... )
        >>> exporter = OpenTelemetryExporter(config)
        >>> exporter.start()
    """
    return OpenTelemetryConfig(
        service_name=service_name,
        backend="datadog",
        datadog_site=site,
        headers={"DD-API-KEY": api_key},
        enable_traces=True,
        enable_metrics=True,
    )


def create_newrelic_config(
    service_name: str = "agent-monitor",
    api_key: str = "",
) -> OpenTelemetryConfig:
    """
    Create config for New Relic backend.

    New Relic is a full-stack observability platform.

    Setup:
        1. Get Ingest License Key from https://one.newrelic.com/api-keys
        2. Set NEW_RELIC_API_KEY environment variable

    View data: https://one.newrelic.com/

    Example:
        >>> import os
        >>> config = create_newrelic_config(
        ...     service_name="my-agent",
        ...     api_key=os.getenv("NEW_RELIC_API_KEY"),
        ... )
        >>> exporter = OpenTelemetryExporter(config)
        >>> exporter.start()
    """
    return OpenTelemetryConfig(
        service_name=service_name,
        backend="newrelic",
        newrelic_api_key=api_key,
        enable_traces=True,
        enable_metrics=True,
    )


def create_otlp_config(
    service_name: str = "agent-monitor",
    endpoint: str = "http://localhost:4317",
    headers: Optional[Dict[str, str]] = None,
) -> OpenTelemetryConfig:
    """
    Create config for generic OTLP backend.

    OTLP (OpenTelemetry Protocol) is the standard protocol for exporting
    telemetry data. Use this for:
    - Grafana Cloud
    - Prometheus
    - Custom OTLP collectors
    - OpenTelemetry Collector

    Setup:
        docker run -d --name otel-collector \\
          -p 4317:4317 \\
          otel/opentelemetry-collector:latest

    Example:
        >>> config = create_otlp_config(
        ...     service_name="my-agent",
        ...     endpoint="http://otel-collector:4317",
        ... )
        >>> exporter = OpenTelemetryExporter(config)
        >>> exporter.start()
    """
    return OpenTelemetryConfig(
        service_name=service_name,
        backend="otlp",
        endpoint=endpoint,
        headers=headers or {},
        enable_traces=True,
        enable_metrics=True,
    )
