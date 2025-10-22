# OpenTelemetry Integration Examples

Production-ready examples showing how to integrate Agent Monitor with popular observability platforms via OpenTelemetry.

## 🎯 Overview

OpenTelemetry is the industry-standard observability framework. These examples show how to export Agent Monitor telemetry to enterprise monitoring platforms:

| Platform | Type | Best For | Open Source | Pricing |
|----------|------|----------|-------------|---------|
| **Jaeger** | Distributed Tracing | Local development, self-hosted | ✅ Yes | Free |
| **Datadog** | Full-Stack APM | Enterprise monitoring | ❌ Commercial | ~$15/host/month |
| **New Relic** | Full-Stack Observability | Application performance | ❌ Commercial | ~$99/month |
| **Grafana Cloud** | Dashboards & Metrics | Visualization | ✅/❌ Hybrid | Free tier available |
| **Prometheus** | Metrics & Alerting | Kubernetes, cloud-native | ✅ Yes | Free |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Agent Monitor with OpenTelemetry support
pip install agent-monitor opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# For Jaeger
pip install opentelemetry-exporter-jaeger

# For Prometheus
pip install prometheus-client
```

### Choose Your Backend

#### 1. Jaeger (Open Source)

**Best for**: Local development, self-hosted deployments, free distributed tracing

```bash
# Start Jaeger
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 6831:6831/udp \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest

# Run example
python jaeger_example.py

# View traces
open http://localhost:16686
```

**Features**:
- ✅ Free and open source
- ✅ Beautiful trace visualization
- ✅ Service dependency graphs
- ✅ No API keys required
- ✅ Self-hosted (no data leaves your network)

---

#### 2. Datadog (Commercial)

**Best for**: Enterprise monitoring, production deployments, teams already using Datadog

```bash
# Get API key from https://app.datadoghq.com/organization-settings/api-keys
export DD_API_KEY=your_api_key_here

# Run example
python datadog_example.py

# View data
open https://app.datadoghq.com/apm/traces
```

**Features**:
- ✅ Full-stack APM (traces, metrics, logs)
- ✅ AI-powered anomaly detection
- ✅ Cost tracking and forecasting
- ✅ 200+ integrations
- ✅ Mobile app for on-call monitoring
- ✅ Advanced alerting and dashboards

**Pricing**: ~$15/host/month + $0.05/GB ingested

---

#### 3. New Relic (Commercial)

**Best for**: Application performance monitoring, full-stack observability

```bash
# Get Ingest License Key from https://one.newrelic.com/api-keys
export NEW_RELIC_API_KEY=your_ingest_license_key

# Run example
python newrelic_example.py

# View data
open https://one.newrelic.com/
```

**Features**:
- ✅ Full-stack observability
- ✅ AI-powered insights (New Relic AI)
- ✅ Automatic instrumentation
- ✅ Vulnerability management
- ✅ Custom dashboards and queries (NRQL)
- ✅ Generous free tier (100 GB/month)

**Pricing**: Free tier available, paid starts at $99/month

---

## 📊 What Gets Exported

### Traces (Distributed Tracing)

Traces capture the complete execution flow of your agents:

```
customer_support_workflow (3.5s, $0.08)
├─ classify_intent (0.5s, $0.01)
│  ├─ model: gpt-4
│  ├─ tokens: 150 in, 20 out
│  └─ confidence: 0.95
├─ search_knowledge_base (0.3s, $0.00)
│  ├─ query: "billing policy"
│  └─ results: 5
├─ route_to_specialist (0.2s, $0.00)
│  └─ specialist: billing_agent_02
├─ generate_response (1.5s, $0.04)
│  ├─ model: gpt-4
│  └─ tokens: 2500 in, 400 out
└─ tool_execution (1.0s, $0.03)
   ├─ check_billing_status (0.4s)
   └─ create_ticket (0.6s)
```

**Attributes captured**:
- Agent name, operation, version
- LLM model, tokens (input/output)
- Cost per operation (USD)
- Success/failure status
- Tool calls and arguments
- Custom metadata

### Metrics

Metrics provide quantitative data over time:

**Request Metrics**:
- `agent.requests.total` - Total requests
- `agent.requests.duration` - Request latency (histogram)
- `agent.requests.errors` - Error count

**Cost Metrics**:
- `agent.cost.total_usd` - Total cost
- `agent.cost.per_request` - Cost per request (histogram)

**Token Metrics**:
- `agent.tokens.input` - Input tokens consumed
- `agent.tokens.output` - Output tokens generated

**Tool Metrics**:
- `agent.tools.calls` - Tool invocations

All metrics include labels for:
- `agent.name` - Agent identifier
- `agent.operation` - Operation type
- `agent.environment` - Environment (prod/staging/dev)
- `agent.version` - Agent version

---

## 🔧 Advanced Configuration

### Custom Resource Attributes

Add metadata to all telemetry:

```python
from agent_monitor.exporters import OpenTelemetryConfig, OpenTelemetryExporter

config = OpenTelemetryConfig(
    service_name="my-agent",
    endpoint="http://localhost:4317",
    resource_attributes={
        "deployment.environment": "production",
        "service.namespace": "ai-agents",
        "service.instance.id": "agent-01",
        "cloud.provider": "aws",
        "cloud.region": "us-east-1",
        "team": "ml-platform",
    }
)

exporter = OpenTelemetryExporter(config)
exporter.start()
```

### Multi-Backend Export

Export to multiple backends simultaneously:

```python
# Export to Jaeger (traces) + Prometheus (metrics)
jaeger_config = create_jaeger_config(service_name="my-agent")
jaeger_exporter = OpenTelemetryExporter(jaeger_config)
jaeger_exporter.start()

prometheus_config = PrometheusConfig(port=9090)
prometheus_exporter = PrometheusExporter(prometheus_config)
prometheus_exporter.start()

# Both exporters run in parallel
```

### Sampling for Cost Reduction

Reduce telemetry volume in high-traffic systems:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

config = OpenTelemetryConfig(
    service_name="my-agent",
    endpoint="http://localhost:4317",
)

# Sample 10% of traces
exporter = OpenTelemetryExporter(config)
# Configure sampler in TracerProvider setup
```

---

## 📈 Best Practices

### 1. Use Consistent Naming

```python
# ✅ Good: Consistent, hierarchical names
with exporter.trace_operation("agent.classify_intent") as span:
    pass

with exporter.trace_operation("agent.generate_response") as span:
    pass

# ❌ Bad: Inconsistent naming
with exporter.trace_operation("ClassifyIntent") as span:
    pass

with exporter.trace_operation("gen-resp") as span:
    pass
```

### 2. Add Rich Context

```python
# ✅ Good: Rich context for debugging
span.set_attribute("agent.name", "customer_support")
span.set_attribute("agent.version", "1.2.3")
span.set_attribute("llm.model", "gpt-4")
span.set_attribute("llm.tokens.input", 1500)
span.set_attribute("customer.id", "cust_12345")
span.set_attribute("customer.tier", "premium")

# ❌ Bad: Minimal context
span.set_attribute("agent", "cs")
```

### 3. Track Costs

```python
# ✅ Good: Track costs per operation
exporter.export_agent_execution(
    agent_name="customer_support",
    operation="handle_inquiry",
    duration_seconds=2.3,
    cost_usd=0.05,  # Important for budgeting!
    tokens_input=1500,
    tokens_output=500,
    success=True,
)
```

### 4. Use Structured Errors

```python
# ✅ Good: Structured error tracking
try:
    result = agent.run(query)
except RateLimitError as e:
    span.set_status(Status(StatusCode.ERROR, "Rate limit exceeded"))
    span.set_attribute("error.type", "RateLimitError")
    span.set_attribute("error.message", str(e))
    span.set_attribute("error.retry_after_seconds", e.retry_after)
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.set_attribute("error.type", type(e).__name__)
```

---

## 🎯 Use Cases

### 1. Cost Optimization

**Problem**: AI agents are expensive, need to track and reduce costs

**Solution**: Export cost metrics to Datadog/New Relic, create cost dashboards

```python
# Track costs per agent
exporter.record_metric(
    "agent.cost.total_usd",
    0.05,
    {"agent": "customer_support", "model": "gpt-4"}
)

# Set up alerts in Datadog/New Relic:
# - Alert if daily cost > $100
# - Alert if cost per request > $0.10
```

**Result**: Identify expensive operations, optimize prompts, switch to cheaper models where appropriate

---

### 2. Performance Debugging

**Problem**: Some agent executions are slow, need to find bottlenecks

**Solution**: Use distributed tracing in Jaeger/Datadog to visualize execution flow

```python
# Trace entire workflow
with exporter.trace_operation("customer_support_workflow") as workflow:
    with exporter.trace_operation("classify_intent") as step1:
        pass  # 0.5s
    with exporter.trace_operation("search_knowledge_base") as step2:
        pass  # 2.5s ← BOTTLENECK!
    with exporter.trace_operation("generate_response") as step3:
        pass  # 1.0s
```

**Result**: Visualize traces, identify that `search_knowledge_base` is slow, optimize vector search

---

### 3. Error Tracking

**Problem**: Agents occasionally fail, need to understand why

**Solution**: Export error traces with context to debug failures

```python
try:
    result = agent.run(query)
except Exception as e:
    exporter.export_agent_execution(
        agent_name="customer_support",
        operation="handle_inquiry",
        duration_seconds=1.2,
        cost_usd=0.02,
        tokens_input=500,
        tokens_output=0,
        success=False,
        error=str(e),
        metadata={"customer_id": "cust_12345", "query": query},
    )
```

**Result**: Get alerts on errors, view error traces with full context for debugging

---

### 4. Multi-Agent Orchestration

**Problem**: Complex workflows with multiple agents, need to track coordination

**Solution**: Use distributed tracing to visualize agent interactions

```python
with exporter.trace_operation("order_processing") as root:
    # Agent 1
    with exporter.trace_operation("fraud_detection") as a1:
        pass
    # Agent 2
    with exporter.trace_operation("inventory_check") as a2:
        pass
    # Agent 3
    with exporter.trace_operation("pricing_optimization") as a3:
        pass
```

**Result**: Visualize complete workflow, understand agent coordination, optimize orchestration

---

## 🐛 Troubleshooting

### Issue: No data appearing in backend

**Solution 1**: Check exporter started successfully
```python
exporter.start()  # Make sure this is called!
```

**Solution 2**: Verify endpoint is correct
```bash
# Test connection
curl http://localhost:4317  # Should not immediately fail
```

**Solution 3**: Check API keys (Datadog, New Relic)
```bash
echo $DD_API_KEY          # Should print your key
echo $NEW_RELIC_API_KEY   # Should print your key
```

**Solution 4**: Wait 1-2 minutes for data to appear
- Most backends have ingestion delay
- Check backend status page for issues

---

### Issue: High telemetry costs

**Solution 1**: Reduce sampling rate
```python
# Sample 10% of traces instead of 100%
# (configure in TracerProvider)
```

**Solution 2**: Export only metrics (not traces)
```python
config = OpenTelemetryConfig(
    enable_traces=False,  # Disable traces
    enable_metrics=True,   # Keep metrics
)
```

**Solution 3**: Use open-source backends (Jaeger + Prometheus)
- No per-GB ingestion costs
- Self-hosted, no vendor lock-in

---

### Issue: Performance overhead

**Solution 1**: Use batch export (default)
- OpenTelemetry batches data automatically
- Minimal performance impact (< 1ms per operation)

**Solution 2**: Export asynchronously
```python
# Telemetry export happens in background thread
# Your agent code is not blocked
```

**Solution 3**: Disable in development
```python
import os

if os.getenv("ENVIRONMENT") == "production":
    exporter.start()
```

---

## 📚 Additional Resources

### Documentation
- [OpenTelemetry Docs](https://opentelemetry.io/docs/)
- [Jaeger Docs](https://www.jaegertracing.io/docs/)
- [Datadog APM Docs](https://docs.datadoghq.com/tracing/)
- [New Relic Docs](https://docs.newrelic.com/)

### Tutorials
- [OpenTelemetry Python Guide](https://opentelemetry.io/docs/instrumentation/python/)
- [Distributed Tracing Best Practices](https://opentelemetry.io/docs/concepts/observability-primer/)

### Tools
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) - Central telemetry pipeline
- [Grafana](https://grafana.com/) - Open-source dashboards
- [Prometheus](https://prometheus.io/) - Open-source metrics

---

## 🤝 Contributing

Want to add more examples?

1. Create new file: `examples/opentelemetry-integration/{backend}_example.py`
2. Follow naming conventions (lowercase, underscores)
3. Include setup instructions in docstring
4. Add to this README
5. Test with real backend
6. Submit PR

**Most wanted examples**:
- AWS X-Ray integration
- Google Cloud Trace integration
- Grafana Cloud integration
- Splunk integration
- Elasticsearch APM integration

---

**Built with ❤️ by Cognio AI Lab**

*Make AI agents observable with enterprise-grade telemetry.*
