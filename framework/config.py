"""
Configuration classes for Enterprise MCP Framework
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider types"""
    OAUTH = "oauth"
    API_KEY = "api_key"
    SAML = "saml"
    LDAP = "ldap"


class ComplianceTemplate(str, Enum):
    """Compliance template types"""
    SOX = "sox"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"


@dataclass
class SecurityConfig:
    """Security layer configuration"""

    # Authentication
    auth_provider: AuthProvider = AuthProvider.API_KEY
    auth_config: Dict[str, Any] = field(default_factory=dict)

    # Authorization
    rbac_enabled: bool = True
    roles_config: Optional[str] = None  # Path to roles YAML

    # Encryption
    tls_enabled: bool = True
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    at_rest_encryption: bool = False

    # Secrets Management
    secrets_manager: Optional[str] = None  # vault, aws_secrets, azure_keyvault
    secrets_config: Dict[str, Any] = field(default_factory=dict)

    # Tenant Isolation (for multi-tenant)
    tenant_isolation: bool = False


@dataclass
class MetricsConfig:
    """Metrics configuration"""
    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class TracingConfig:
    """Tracing configuration"""
    enabled: bool = True
    provider: str = "opentelemetry"  # opentelemetry, jaeger, zipkin
    endpoint: Optional[str] = None
    sample_rate: float = 1.0  # 0.0 to 1.0


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"  # DEBUG, INFO, WARN, ERROR
    format: str = "json"  # json, text
    output: str = "stdout"  # stdout, file, syslog


@dataclass
class ObservabilityConfig:
    """Observability layer configuration"""

    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    dashboard_enabled: bool = True
    dashboard_port: int = 3000


@dataclass
class ApprovalConfig:
    """Approval workflow configuration"""
    name: str
    operations: List[str]  # List of operations requiring approval
    approvers: List[str]  # slack:#channel, email:user@domain.com, jira:PROJECT
    required_approvals: int = 1
    timeout_seconds: int = 3600  # 1 hour default


@dataclass
class AuditConfig:
    """Audit logging configuration"""
    enabled: bool = True
    storage: str = "postgresql"  # postgresql, elasticsearch, s3
    storage_config: Dict[str, Any] = field(default_factory=dict)
    retention_days: int = 365  # 1 year default


@dataclass
class PolicyConfig:
    """Policy engine configuration"""
    enabled: bool = True
    engine: str = "opa"  # Open Policy Agent
    policy_dir: Optional[str] = None


@dataclass
class GovernanceConfig:
    """Governance layer configuration"""

    approvals: List[ApprovalConfig] = field(default_factory=list)
    audit: AuditConfig = field(default_factory=AuditConfig)
    policies: PolicyConfig = field(default_factory=PolicyConfig)

    # Compliance
    compliance_template: Optional[ComplianceTemplate] = None
    compliance_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = True
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    per_user: bool = True


@dataclass
class BudgetConfig:
    """Budget configuration"""
    enabled: bool = True
    monthly_limit_usd: float = 1000.0
    alert_threshold: float = 0.8  # Alert at 80%
    alert_channels: List[str] = field(default_factory=lambda: ["email"])


@dataclass
class CostConfig:
    """Cost management layer configuration"""

    tracking_enabled: bool = True
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)

    # Cost allocation
    per_tenant_tracking: bool = False
    chargeback_enabled: bool = False


@dataclass
class FrameworkConfig:
    """Complete framework configuration"""

    # Target MCP server
    target_server: str
    target_host: str = "localhost"
    target_port: int = 8080

    # Framework layers
    security: SecurityConfig = field(default_factory=SecurityConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    cost_management: CostConfig = field(default_factory=CostConfig)

    # Proxy settings
    proxy_host: str = "0.0.0.0"
    proxy_port: int = 8000
    workers: int = 4

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.target_server:
            raise ValueError("target_server is required")

        if self.security.tls_enabled:
            if not self.security.tls_cert_path or not self.security.tls_key_path:
                raise ValueError("TLS enabled but cert/key paths not provided")

        return True
