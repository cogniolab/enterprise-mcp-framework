"""
Enterprise MCP Proxy Server
Transparent proxy that adds enterprise features to any MCP server
"""

import asyncio
import logging
from typing import Optional, Any, Dict
import json

from ..config import FrameworkConfig, SecurityConfig, ObservabilityConfig, GovernanceConfig, CostConfig
from .middleware import MiddlewareChain, Request, Response
from .router import MCPRouter

# Middleware imports
from ..security.middleware import SecurityMiddleware
from ..observability.middleware import ObservabilityMiddleware
from ..governance.middleware import GovernanceMiddleware
from ..cost_management.middleware import CostManagementMiddleware

logger = logging.getLogger(__name__)


class EnterpriseProxy:
    """
    Enterprise MCP Proxy Server

    Acts as a transparent proxy between LLM applications and MCP servers,
    adding security, observability, governance, and cost management.

    Example:
        >>> proxy = EnterpriseProxy(
        ...     target_server="postgresql-mcp",
        ...     security=SecurityConfig(auth_provider="oauth"),
        ...     observability=ObservabilityConfig(metrics=True)
        ... )
        >>> proxy.start()
    """

    def __init__(
        self,
        target_server: str,
        target_host: str = "localhost",
        target_port: int = 8080,
        security: Optional[SecurityConfig] = None,
        observability: Optional[ObservabilityConfig] = None,
        governance: Optional[GovernanceConfig] = None,
        cost_management: Optional[CostConfig] = None,
        proxy_host: str = "0.0.0.0",
        proxy_port: int = 8000,
    ):
        """
        Initialize Enterprise MCP Proxy

        Args:
            target_server: Name/identifier of target MCP server
            target_host: Host of target MCP server
            target_port: Port of target MCP server
            security: Security configuration
            observability: Observability configuration
            governance: Governance configuration
            cost_management: Cost management configuration
            proxy_host: Proxy server host
            proxy_port: Proxy server port
        """
        self.config = FrameworkConfig(
            target_server=target_server,
            target_host=target_host,
            target_port=target_port,
            security=security or SecurityConfig(),
            observability=observability or ObservabilityConfig(),
            governance=governance or GovernanceConfig(),
            cost_management=cost_management or CostConfig(),
            proxy_host=proxy_host,
            proxy_port=proxy_port,
        )

        # Validate configuration
        self.config.validate()

        # Initialize components
        self.router = MCPRouter(target_host, target_port)
        self.middleware = self._init_middleware()

        logger.info(f"Enterprise MCP Proxy initialized for {target_server}")

    def _init_middleware(self) -> MiddlewareChain:
        """Initialize middleware chain"""
        chain = MiddlewareChain()

        # Add middleware in order:
        # Security → Observability → Governance → Cost Management

        # 1. Security layer (auth, RBAC, encryption)
        if self.config.security:
            chain.add(SecurityMiddleware(self.config.security))
            logger.info("Security middleware enabled")

        # 2. Observability layer (metrics, tracing, logging)
        if self.config.observability:
            chain.add(ObservabilityMiddleware(self.config.observability))
            logger.info("Observability middleware enabled")

        # 3. Governance layer (approvals, audit, policies)
        if self.config.governance:
            chain.add(GovernanceMiddleware(self.config.governance))
            logger.info("Governance middleware enabled")

        # 4. Cost management layer (tracking, limits, budgets)
        if self.config.cost_management:
            chain.add(CostManagementMiddleware(self.config.cost_management))
            logger.info("Cost management middleware enabled")

        return chain

    async def handle_request(self, raw_request: bytes) -> bytes:
        """
        Handle MCP request through middleware chain

        Args:
            raw_request: Raw MCP protocol request

        Returns:
            Raw MCP protocol response
        """
        try:
            # Parse MCP request
            request = Request.from_bytes(raw_request)

            logger.debug(f"Processing request: {request.method}")

            # Process through middleware chain
            processed_request = await self.middleware.process_request(request)

            # Forward to target MCP server
            raw_response = await self.router.forward(processed_request.to_bytes())

            # Parse response
            response = Response.from_bytes(raw_response)

            # Process response through middleware chain
            processed_response = await self.middleware.process_response(response, request)

            return processed_response.to_bytes()

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            # Return error response
            error_response = Response.error(str(e))
            return error_response.to_bytes()

    def start(self):
        """
        Start the Enterprise MCP Proxy server

        This starts an async server that listens for MCP protocol connections
        and proxies them through the middleware chain to the target server.
        """
        logger.info(f"Starting Enterprise MCP Proxy on {self.config.proxy_host}:{self.config.proxy_port}")
        logger.info(f"Target server: {self.config.target_server} at {self.config.target_host}:{self.config.target_port}")

        # Start async event loop
        asyncio.run(self._run_server())

    async def _run_server(self):
        """Run the proxy server"""
        # Create TCP server
        server = await asyncio.start_server(
            self._handle_connection,
            self.config.proxy_host,
            self.config.proxy_port
        )

        addr = server.sockets[0].getsockname()
        logger.info(f"Proxy server listening on {addr}")

        async with server:
            await server.serve_forever()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connection"""
        addr = writer.get_extra_info('peername')
        logger.debug(f"Connection from {addr}")

        try:
            while True:
                # Read request
                data = await reader.read(4096)
                if not data:
                    break

                # Process through enterprise layers
                response = await self.handle_request(data)

                # Send response
                writer.write(response)
                await writer.drain()

        except Exception as e:
            logger.error(f"Error handling connection from {addr}: {e}")

        finally:
            writer.close()
            await writer.wait_closed()
            logger.debug(f"Connection closed: {addr}")

    def stop(self):
        """Stop the proxy server"""
        logger.info("Stopping Enterprise MCP Proxy")
        # Cleanup resources
        # TODO: Implement graceful shutdown


# Convenience function
def create_proxy(
    target_server: str,
    **kwargs
) -> EnterpriseProxy:
    """
    Create an Enterprise MCP Proxy with sensible defaults

    Args:
        target_server: Target MCP server name
        **kwargs: Additional configuration options

    Returns:
        Configured EnterpriseProxy instance
    """
    return EnterpriseProxy(target_server=target_server, **kwargs)
