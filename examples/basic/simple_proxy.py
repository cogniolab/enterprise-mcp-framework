"""
Simple example of Enterprise MCP Framework

This example shows how to wrap any MCP server with enterprise features
in just a few lines of code.
"""

import asyncio
from framework import EnterpriseProxy, SecurityConfig, ObservabilityConfig


async def main():
    """Run simple enterprise MCP proxy"""

    # Create proxy with enterprise features
    proxy = EnterpriseProxy(
        target_server="my-mcp-server",
        target_host="localhost",
        target_port=8080,

        # Enable security
        security=SecurityConfig(
            auth_provider="api_key",
            rbac_enabled=True
        ),

        # Enable observability
        observability=ObservabilityConfig(
            metrics=True,
            tracing=True
        )
    )

    print("✅ Enterprise MCP Proxy configured!")
    print(f"🔒 Security: Authentication ({proxy.config.security.auth_provider}), RBAC")
    print(f"📊 Observability: Metrics, Tracing, Logging")
    print(f"🎯 Target: {proxy.config.target_server}")
    print(f"🌐 Listening on: {proxy.config.proxy_host}:{proxy.config.proxy_port}")
    print("\nStarting proxy server...")

    # Start the proxy
    proxy.start()


if __name__ == "__main__":
    asyncio.run(main())
