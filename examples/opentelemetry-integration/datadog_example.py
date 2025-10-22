"""
Datadog Integration Example

Demonstrates how to export Agent Monitor telemetry to Datadog APM.

Datadog is a commercial monitoring and analytics platform for cloud applications.

Setup:
    1. Get Datadog API key:
       - Sign up at https://www.datadoghq.com
       - Get API key from https://app.datadoghq.com/organization-settings/api-keys

    2. Set environment variable:
       export DD_API_KEY=your_api_key_here

    3. Install dependencies:
       pip install agent-monitor opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

    4. Run this example:
       python datadog_example.py

    5. View data:
       - Traces: https://app.datadoghq.com/apm/traces
       - Metrics: https://app.datadoghq.com/metric/explorer
       - Dashboards: https://app.datadoghq.com/dashboard/lists
"""

import os
import time
from agent_monitor import AgentMonitor
from agent_monitor.exporters import OpenTelemetryExporter, create_datadog_config


def main():
    """Run agent with Datadog monitoring."""
    dd_api_key = os.getenv("DD_API_KEY")
    if not dd_api_key:
        print("❌ Error: DD_API_KEY environment variable not set")
        print("   Get your API key from: https://app.datadoghq.com/organization-settings/api-keys")
        print("   Then run: export DD_API_KEY=your_api_key")
        return

    print("🚀 Starting Agent Monitor with Datadog integration...")

    # Create Datadog exporter
    otel_config = create_datadog_config(
        service_name="ai-agent-production",
        api_key=dd_api_key,
        site="datadoghq.com",  # Use "datadoghq.eu" for EU region
    )

    otel_exporter = OpenTelemetryExporter(otel_config)
    otel_exporter.start()

    print("✅ Datadog exporter started")
    print("📊 View data at:")
    print("   - Traces: https://app.datadoghq.com/apm/traces")
    print("   - Metrics: https://app.datadoghq.com/metric/explorer")
    print()

    # Simulate production workload
    simulate_production_workload(otel_exporter)

    print()
    print("✅ Example complete!")
    print("📊 Check Datadog APM to see your agent traces and metrics")
    print("   It may take 1-2 minutes for data to appear")

    # Flush telemetry
    otel_exporter.shutdown()


def simulate_production_workload(exporter: OpenTelemetryExporter):
    """Simulate a production agent workload with multiple executions."""
    print("🤖 Simulating production AI agent workload...")

    agents = [
        ("sales_assistant", "qualify_lead"),
        ("customer_support", "handle_inquiry"),
        ("data_analyst", "generate_report"),
    ]

    for i in range(5):
        agent_name, operation = agents[i % len(agents)]

        print(f"  {i+1}. Running {agent_name}.{operation}...")

        # Simulate execution
        start_time = time.time()
        success = True
        error = None

        try:
            with exporter.trace_operation(f"{agent_name}.{operation}") as span:
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.operation", operation)
                span.set_attribute("agent.environment", "production")
                span.set_attribute("agent.version", "1.2.3")

                # Simulate LLM call
                duration = 0.5 + (i * 0.2)
                time.sleep(duration)

                # Add execution details
                span.set_attribute("llm.model", "gpt-4-turbo")
                span.set_attribute("llm.tokens.input", 1000 + (i * 200))
                span.set_attribute("llm.tokens.output", 300 + (i * 50))

                # Simulate occasional errors
                if i == 3:
                    success = False
                    error = "Rate limit exceeded"
                    raise Exception(error)

        except Exception as e:
            success = False
            error = str(e)

        duration = time.time() - start_time

        # Calculate costs (example pricing)
        tokens_input = 1000 + (i * 200)
        tokens_output = 300 + (i * 50)
        cost_usd = (tokens_input / 1_000_000 * 10) + (tokens_output / 1_000_000 * 30)

        # Export complete execution
        exporter.export_agent_execution(
            agent_name=agent_name,
            operation=operation,
            duration_seconds=duration,
            cost_usd=cost_usd,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            success=success,
            error=error,
            metadata={
                "environment": "production",
                "version": "1.2.3",
                "region": "us-east-1",
            },
        )

        time.sleep(0.5)  # Pause between executions

    print("  ✅ Workload simulation complete!")


def demonstrate_custom_metrics(exporter: OpenTelemetryExporter):
    """Demonstrate custom metric recording."""
    print()
    print("📊 Recording custom metrics...")

    # Business metrics
    exporter.record_metric(
        "agent.business.leads_qualified",
        1,
        {"agent": "sales_assistant", "source": "website"}
    )

    exporter.record_metric(
        "agent.business.tickets_resolved",
        1,
        {"agent": "customer_support", "priority": "high"}
    )

    # Performance metrics
    exporter.record_metric(
        "agent.performance.accuracy",
        0.95,
        {"agent": "data_analyst", "task": "classification"}
    )

    exporter.record_metric(
        "agent.performance.user_satisfaction",
        4.8,
        {"agent": "customer_support", "scale": "5"}
    )

    print("  ✅ Custom metrics recorded")


if __name__ == "__main__":
    main()
