"""
Jaeger Integration Example

Demonstrates how to export Agent Monitor telemetry to Jaeger for distributed tracing.

Jaeger is an open-source, end-to-end distributed tracing system.

Setup:
    1. Start Jaeger all-in-one container:
       docker run -d --name jaeger \
         -e COLLECTOR_OTLP_ENABLED=true \
         -p 6831:6831/udp \
         -p 6832:6832/udp \
         -p 5778:5778 \
         -p 16686:16686 \
         -p 4317:4317 \
         -p 4318:4318 \
         -p 14250:14250 \
         -p 14268:14268 \
         -p 14269:14269 \
         -p 9411:9411 \
         jaegertracing/all-in-one:latest

    2. Install dependencies:
       pip install agent-monitor opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger

    3. Run this example:
       python jaeger_example.py

    4. View traces:
       http://localhost:16686
"""

import time
from agent_monitor import AgentMonitor
from agent_monitor.exporters import OpenTelemetryExporter, create_jaeger_config


def main():
    """Run agent with Jaeger tracing."""
    print("🚀 Starting Agent Monitor with Jaeger integration...")

    # Create Jaeger exporter
    otel_config = create_jaeger_config(
        service_name="customer-support-agent",
        agent_host="localhost",
        agent_port=6831,
    )

    otel_exporter = OpenTelemetryExporter(otel_config)
    otel_exporter.start()

    print("✅ Jaeger exporter started")
    print("📊 View traces at: http://localhost:16686")
    print()

    # Simulate agent operations
    simulate_agent_workflow(otel_exporter)

    print()
    print("✅ Example complete!")
    print("📊 Check Jaeger UI at http://localhost:16686 to see traces")

    # Flush telemetry
    otel_exporter.shutdown()


def simulate_agent_workflow(exporter: OpenTelemetryExporter):
    """Simulate a multi-step agent workflow."""
    print("🤖 Simulating customer support agent workflow...")

    # Root trace: Customer support workflow
    with exporter.trace_operation("customer_support_workflow") as workflow_span:
        workflow_span.set_attribute("customer.id", "cust_12345")
        workflow_span.set_attribute("customer.tier", "premium")

        # Step 1: Classify intent
        print("  1️⃣ Classifying customer intent...")
        with exporter.trace_operation("classify_intent") as intent_span:
            time.sleep(0.5)  # Simulate LLM call
            intent_span.set_attribute("intent.detected", "billing_question")
            intent_span.set_attribute("intent.confidence", 0.95)
            intent_span.set_attribute("llm.model", "gpt-4")
            intent_span.set_attribute("llm.tokens.input", 150)
            intent_span.set_attribute("llm.tokens.output", 20)

        # Step 2: Search knowledge base
        print("  2️⃣ Searching knowledge base...")
        with exporter.trace_operation("search_knowledge_base") as search_span:
            time.sleep(0.3)  # Simulate vector search
            search_span.set_attribute("search.query", "billing policy")
            search_span.set_attribute("search.results_count", 5)
            search_span.set_attribute("search.top_score", 0.89)

        # Step 3: Route to specialist
        print("  3️⃣ Routing to specialist agent...")
        with exporter.trace_operation("route_to_specialist") as route_span:
            time.sleep(0.2)
            route_span.set_attribute("specialist.type", "billing")
            route_span.set_attribute("specialist.agent_id", "billing_agent_02")

        # Step 4: Generate response
        print("  4️⃣ Generating response...")
        with exporter.trace_operation("generate_response") as response_span:
            time.sleep(1.5)  # Simulate LLM call
            response_span.set_attribute("llm.model", "gpt-4")
            response_span.set_attribute("llm.tokens.input", 2500)
            response_span.set_attribute("llm.tokens.output", 400)
            response_span.set_attribute("response.length_chars", 1200)

        # Step 5: Tool calls
        print("  5️⃣ Executing tool calls...")
        with exporter.trace_operation("tool_execution") as tool_span:
            # Check billing status
            with exporter.trace_operation("tool.check_billing_status") as check_span:
                time.sleep(0.4)
                check_span.set_attribute("tool.name", "check_billing_status")
                check_span.set_attribute("tool.args", '{"customer_id": "cust_12345"}')
                check_span.set_attribute("tool.result", "active")

            # Create ticket
            with exporter.trace_operation("tool.create_ticket") as ticket_span:
                time.sleep(0.6)
                ticket_span.set_attribute("tool.name", "create_ticket")
                ticket_span.set_attribute("tool.args", '{"title": "Billing inquiry"}')
                ticket_span.set_attribute("tool.result", "TICKET-789")

            tool_span.set_attribute("tools.count", 2)
            tool_span.set_attribute("tools.names", '["check_billing_status", "create_ticket"]')

        # Record final metrics
        workflow_span.set_attribute("workflow.total_duration_seconds", 3.5)
        workflow_span.set_attribute("workflow.cost_usd", 0.08)
        workflow_span.set_attribute("workflow.success", True)

    # Export complete execution
    exporter.export_agent_execution(
        agent_name="customer_support",
        operation="handle_inquiry",
        duration_seconds=3.5,
        cost_usd=0.08,
        tokens_input=2650,
        tokens_output=420,
        success=True,
        tool_calls=["check_billing_status", "create_ticket"],
        metadata={
            "customer_id": "cust_12345",
            "customer_tier": "premium",
            "intent": "billing_question",
        },
    )

    print("  ✅ Workflow complete!")


if __name__ == "__main__":
    main()
