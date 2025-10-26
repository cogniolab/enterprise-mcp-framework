import pytest
from unittest.mock import Mock, patch, AsyncMock
from enterprise_mcp_framework.security import SecurityManager
from enterprise_mcp_framework.observability import ObservabilityManager
from enterprise_mcp_framework.governance import GovernanceManager


class TestSecurityManager:
    """Test cases for SecurityManager with production patterns."""

    @pytest.fixture
    def security_manager(self):
        """Initialize SecurityManager with test configuration."""
        return SecurityManager(
            api_key_secret="test-secret-key",
            encryption_enabled=True,
            audit_logging=True
        )

    @pytest.mark.asyncio
    async def test_validate_request_with_valid_token(self, security_manager):
        """Test successful request validation with valid authentication token."""
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        request = Mock(headers={"Authorization": f"Bearer {valid_token}"})
        
        result = await security_manager.validate_request(request)
        assert result.is_valid is True
        assert result.principal_id is not None

    @pytest.mark.asyncio
    async def test_validate_request_with_invalid_token(self, security_manager):
        """Test request validation fails with invalid token."""
        request = Mock(headers={"Authorization": "Bearer invalid-token"})
        
        result = await security_manager.validate_request(request)
        assert result.is_valid is False
        assert result.error_code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data(self, security_manager):
        """Test encryption of sensitive data."""
        sensitive_data = {"api_key": "secret123", "password": "pass456"}
        
        encrypted = await security_manager.encrypt(sensitive_data)
        assert encrypted is not None
        assert encrypted != sensitive_data

    @pytest.mark.asyncio
    async def test_decrypt_sensitive_data(self, security_manager):
        """Test decryption returns original data."""
        original = {"api_key": "secret123"}
        encrypted = await security_manager.encrypt(original)
        
        decrypted = await security_manager.decrypt(encrypted)
        assert decrypted == original


class TestObservabilityManager:
    """Test cases for ObservabilityManager."""

    @pytest.fixture
    def observability_manager(self):
        """Initialize ObservabilityManager."""
        return ObservabilityManager(
            enable_tracing=True,
            enable_metrics=True,
            log_level="INFO"
        )

    @pytest.mark.asyncio
    async def test_trace_request_lifecycle(self, observability_manager):
        """Test tracing captures complete request lifecycle."""
        with observability_manager.trace_context("test_operation") as trace:
            trace.add_span("auth_validation", duration_ms=10)
            trace.add_span("business_logic", duration_ms=50)
            
            result = trace.get_summary()
            assert result.total_duration_ms == 60
            assert len(result.spans) == 2

    @pytest.mark.asyncio
    async def test_metrics_collection(self, observability_manager):
        """Test metrics are correctly collected."""
        await observability_manager.record_metric("request_count", 1, tags={"endpoint": "/test"})
        await observability_manager.record_metric("latency_ms", 125, tags={"endpoint": "/test"})
        
        metrics = observability_manager.get_metrics()
        assert metrics["request_count"] >= 1

    @pytest.mark.asyncio
    async def test_structured_logging(self, observability_manager):
        """Test structured logging format."""
        with patch('enterprise_mcp_framework.observability.logger') as mock_logger:
            await observability_manager.log_event(
                event="REQUEST_PROCESSED",
                level="INFO",
                context={"user_id": "123", "action": "read"}
            )
            mock_logger.info.assert_called_once()


class TestGovernanceManager:
    """Test cases for GovernanceManager."""

    @pytest.fixture
    def governance_manager(self):
        """Initialize GovernanceManager."""
        return GovernanceManager(
            policy_file="policies/default.yaml",
            enforce_policies=True
        )

    @pytest.mark.asyncio
    async def test_policy_evaluation_allowed(self, governance_manager):
        """Test policy evaluation allows permitted operations."""
        request = {
            "principal": "user:123",
            "action": "read",
            "resource": "document:456"
        }
        
        result = await governance_manager.evaluate_policy(request)
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_policy_evaluation_denied(self, governance_manager):
        """Test policy evaluation denies restricted operations."""
        request = {
            "principal": "user:123",
            "action": "delete",
            "resource": "system:config"
        }
        
        result = await governance_manager.evaluate_policy(request)
        assert result.allowed is False
        assert result.denial_reason is not None

    @pytest.mark.asyncio
    async def test_audit_trail_recording(self, governance_manager):
        """Test audit trail records governance decisions."""
        action = {
            "principal": "user:123",
            "action": "write",
            "resource": "document:789",
            "decision": "ALLOWED"
        }
        
        await governance_manager.record_audit(action)
        trail = await governance_manager.get_audit_trail(principal="user:123")
        assert len(trail) > 0
        assert trail[0]["action"] == "write"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])