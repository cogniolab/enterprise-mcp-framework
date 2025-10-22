"""
New Relic Integration Example

Demonstrates how to export Agent Monitor telemetry to New Relic.

New Relic is a full-stack observability platform for monitoring applications.

Setup:
    1. Get New Relic Ingest License Key:
       - Sign up at https://newrelic.com
       - Get key from https://one.newrelic.com/api-keys

    2. Set environment variable:
       export NEW_RELIC_API_KEY=your_ingest_license_key

    3. Install dependencies:
       pip install agent-monitor opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

    4. Run this example:
       python newrelic_example.py

    5. View data:
       - Overview: https://one.newrelic.com/
       - APM: https://one.newrelic.com/apm
       - Distributed Tracing: https://one.newrelic.com/distributed-tracing
"""

import os
import time
from agent_monitor import AgentMonitor
from agent_monitor.exporters import OpenTelemetryExporter, create_newrelic_config


def main():
    """Run agent with New Relic monitoring."""
    nr_api_key = os.getenv("NEW_RELIC_API_KEY")
    if not nr_api_key:
        print("❌ Error: NEW_RELIC_API_KEY environment variable not set")
        print("   Get your Ingest License Key from: https://one.newrelic.com/api-keys")
        print("   Then run: export NEW_RELIC_API_KEY=your_key")
        return

    print("🚀 Starting Agent Monitor with New Relic integration...")

    # Create New Relic exporter
    otel_config = create_newrelic_config(
        service_name="ai-agent-platform",
        api_key=nr_api_key,
    )

    otel_exporter = OpenTelemetryExporter(otel_config)
    otel_exporter.start()

    print("✅ New Relic exporter started")
    print("📊 View data at:")
    print("   - Overview: https://one.newrelic.com/")
    print("   - APM: https://one.newrelic.com/apm")
    print("   - Distributed Tracing: https://one.newrelic.com/distributed-tracing")
    print()

    # Simulate multi-agent system
    simulate_multi_agent_system(otel_exporter)

    print()
    print("✅ Example complete!")
    print("📊 Check New Relic to see your agent telemetry")
    print("   Data should appear within 1-2 minutes")

    # Flush telemetry
    otel_exporter.shutdown()


def simulate_multi_agent_system(exporter: OpenTelemetryExporter):
    """Simulate a multi-agent system with orchestration."""
    print("🤖 Simulating multi-agent system...")

    # Root trace: E-commerce order processing
    with exporter.trace_operation("order_processing_workflow") as workflow_span:
        workflow_span.set_attribute("workflow.type", "e-commerce")
        workflow_span.set_attribute("order.id", "order_98765")
        workflow_span.set_attribute("order.value_usd", 249.99)

        print("  1️⃣ Fraud detection agent...")
        # Agent 1: Fraud detection
        with exporter.trace_operation("fraud_detection_agent") as fraud_span:
            time.sleep(0.8)
            fraud_span.set_attribute("agent.name", "fraud_detector")
            fraud_span.set_attribute("agent.model", "claude-3-opus")
            fraud_span.set_attribute("fraud.risk_score", 0.12)
            fraud_span.set_attribute("fraud.decision", "approved")

            # Record metrics
            exporter.export_agent_execution(
                agent_name="fraud_detector",
                operation="assess_risk",
                duration_seconds=0.8,
                cost_usd=0.02,
                tokens_input=500,
                tokens_output=100,
                success=True,
                metadata={"risk_score": 0.12, "decision": "approved"},
            )

        print("  2️⃣ Inventory management agent...")
        # Agent 2: Inventory check
        with exporter.trace_operation("inventory_management_agent") as inventory_span:
            time.sleep(0.5)
            inventory_span.set_attribute("agent.name", "inventory_manager")
            inventory_span.set_attribute("agent.model", "gpt-4")
            inventory_span.set_attribute("inventory.items_checked", 3)
            inventory_span.set_attribute("inventory.all_available", True)

            exporter.export_agent_execution(
                agent_name="inventory_manager",
                operation="check_availability",
                duration_seconds=0.5,
                cost_usd=0.01,
                tokens_input=300,
                tokens_output=50,
                success=True,
                tool_calls=["query_database", "check_warehouse"],
            )

        print("  3️⃣ Pricing optimization agent...")
        # Agent 3: Pricing optimization
        with exporter.trace_operation("pricing_optimization_agent") as pricing_span:
            time.sleep(0.6)
            pricing_span.set_attribute("agent.name", "pricing_optimizer")
            pricing_span.set_attribute("agent.model", "gpt-4-turbo")
            pricing_span.set_attribute("pricing.discount_applied", 0.10)
            pricing_span.set_attribute("pricing.final_price_usd", 224.99)

            exporter.export_agent_execution(
                agent_name="pricing_optimizer",
                operation="calculate_price",
                duration_seconds=0.6,
                cost_usd=0.015,
                tokens_input=400,
                tokens_output=80,
                success=True,
                metadata={"discount": 0.10, "final_price": 224.99},
            )

        print("  4️⃣ Shipping logistics agent...")
        # Agent 4: Shipping logistics
        with exporter.trace_operation("shipping_logistics_agent") as shipping_span:
            time.sleep(0.7)
            shipping_span.set_attribute("agent.name", "shipping_planner")
            shipping_span.set_attribute("agent.model", "claude-3-sonnet")
            shipping_span.set_attribute("shipping.carrier", "FedEx")
            shipping_span.set_attribute("shipping.estimated_days", 2)

            exporter.export_agent_execution(
                agent_name="shipping_planner",
                operation="plan_shipment",
                duration_seconds=0.7,
                cost_usd=0.012,
                tokens_input=450,
                tokens_output=90,
                success=True,
                tool_calls=["query_carriers", "calculate_routes"],
            )

        print("  5️⃣ Customer notification agent...")
        # Agent 5: Customer notification
        with exporter.trace_operation("customer_notification_agent") as notification_span:
            time.sleep(0.4)
            notification_span.set_attribute("agent.name", "notification_sender")
            notification_span.set_attribute("agent.model", "gpt-3.5-turbo")
            notification_span.set_attribute("notification.channel", "email")
            notification_span.set_attribute("notification.sent", True)

            exporter.export_agent_execution(
                agent_name="notification_sender",
                operation="send_confirmation",
                duration_seconds=0.4,
                cost_usd=0.005,
                tokens_input=250,
                tokens_output=150,
                success=True,
                tool_calls=["send_email"],
            )

        # Record workflow metrics
        workflow_span.set_attribute("workflow.agents_count", 5)
        workflow_span.set_attribute("workflow.total_duration_seconds", 3.0)
        workflow_span.set_attribute("workflow.total_cost_usd", 0.062)
        workflow_span.set_attribute("workflow.success", True)

    print("  ✅ Multi-agent workflow complete!")

    # Record business-level metrics
    print()
    print("📊 Recording business metrics...")

    exporter.record_metric(
        "agent.business.order_processed",
        1,
        {"workflow": "e-commerce", "status": "success"}
    )

    exporter.record_metric(
        "agent.business.order_value_usd",
        224.99,
        {"workflow": "e-commerce"}
    )

    exporter.record_metric(
        "agent.business.fraud_checks_passed",
        1,
        {"agent": "fraud_detector"}
    )

    print("  ✅ Business metrics recorded")


if __name__ == "__main__":
    main()
