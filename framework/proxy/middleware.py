"""
Middleware architecture for Enterprise MCP Framework
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict
from dataclasses import dataclass, field
import json
import time
import uuid


@dataclass
class Request:
    """MCP Request model"""

    method: str
    params: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    jsonrpc: str = "2.0"

    # Metadata added by middleware
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Request":
        """Parse request from bytes"""
        try:
            obj = json.loads(data.decode('utf-8'))
            return cls(
                method=obj.get("method", ""),
                params=obj.get("params", {}),
                id=obj.get("id", str(uuid.uuid4())),
                jsonrpc=obj.get("jsonrpc", "2.0")
            )
        except Exception as e:
            raise ValueError(f"Invalid MCP request: {e}")

    def to_bytes(self) -> bytes:
        """Convert request to bytes"""
        obj = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        }
        return json.dumps(obj).encode('utf-8')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


@dataclass
class Response:
    """MCP Response model"""

    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    jsonrpc: str = "2.0"

    # Metadata added by middleware
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        """Parse response from bytes"""
        try:
            obj = json.loads(data.decode('utf-8'))
            return cls(
                result=obj.get("result"),
                error=obj.get("error"),
                id=obj.get("id"),
                jsonrpc=obj.get("jsonrpc", "2.0")
            )
        except Exception as e:
            raise ValueError(f"Invalid MCP response: {e}")

    def to_bytes(self) -> bytes:
        """Convert response to bytes"""
        obj = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            obj["error"] = self.error
        else:
            obj["result"] = self.result

        return json.dumps(obj).encode('utf-8')

    @classmethod
    def error(cls, message: str, code: int = -32603) -> "Response":
        """Create error response"""
        return cls(
            error={
                "code": code,
                "message": message
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class Middleware(ABC):
    """
    Base class for middleware components

    Middleware can intercept and modify requests and responses,
    add metadata, enforce policies, collect metrics, etc.
    """

    @abstractmethod
    async def process_request(self, request: Request) -> Request:
        """
        Process request before forwarding to target server

        Args:
            request: Incoming request

        Returns:
            Modified request

        Raises:
            Exception: If request should be blocked
        """
        pass

    @abstractmethod
    async def process_response(self, response: Response, request: Request) -> Response:
        """
        Process response before returning to client

        Args:
            response: Response from target server
            request: Original request

        Returns:
            Modified response
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class MiddlewareChain:
    """
    Chain of middleware components

    Processes requests and responses through multiple middleware layers
    in order: Security → Observability → Governance → Cost Management
    """

    def __init__(self):
        self.middleware: List[Middleware] = []

    def add(self, middleware: Middleware):
        """Add middleware to chain"""
        self.middleware.append(middleware)

    async def process_request(self, request: Request) -> Request:
        """Process request through all middleware"""
        for mw in self.middleware:
            request = await mw.process_request(request)
        return request

    async def process_response(self, response: Response, request: Request) -> Response:
        """Process response through all middleware (in reverse order)"""
        for mw in reversed(self.middleware):
            response = await mw.process_response(response, request)
        return response

    def __repr__(self) -> str:
        return f"<MiddlewareChain middleware={[repr(mw) for mw in self.middleware]}>"
