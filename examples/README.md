# Enterprise MCP Server Examples

Production-ready examples demonstrating Enterprise MCP Framework with real-world integrations.

## 📚 Available Examples

### 1. GitHub MCP Server
**Path**: `github-mcp/`
**Description**: Repository management, issues, PRs, code search
**Enterprise Features**:
- RBAC with viewer/developer/admin roles
- Approval workflows for PRs to main branch
- Rate limiting on expensive operations (code search)
- SOC2 compliance with audit logging

**Use Cases**:
- Automated issue triage
- PR review assistance
- Code search for documentation
- Release notes generation

[Full Documentation →](./github-mcp/README.md)

---

### 2. Jira MCP Server
**Path**: `jira-mcp/`
**Description**: Ticket management, sprint planning, JQL search
**Enterprise Features**:
- RBAC with project-level permissions
- Approval workflows for ticket transitions
- SOX compliance with 7-year audit retention
- SLA monitoring and alerts

**Use Cases**:
- AI ticket triage and routing
- Sprint planning assistance
- SLA breach monitoring
- Release planning automation

[Full Documentation →](./jira-mcp/README.md)

---

### 3. Notion MCP Server
**Path**: `notion-mcp/`
**Description**: Knowledge management, documentation, databases
**Enterprise Features**:
- RBAC with workspace isolation
- Approval workflows for page deletion
- GDPR compliance (right to erasure)
- Content access auditing

**Use Cases**:
- AI documentation assistant
- Meeting notes automation
- Project wiki maintenance
- Onboarding bot

[Full Documentation →](./notion-mcp/README.md)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Enterprise MCP Framework
pip install enterprise-mcp-framework

# Install example-specific dependencies
cd github-mcp && pip install -r requirements.txt
cd jira-mcp && pip install -r requirements.txt
cd notion-mcp && pip install -r requirements.txt
```

### Run an Example

```bash
# 1. Set API credentials
export GITHUB_TOKEN=ghp_your_token
# or
export JIRA_URL=https://your-domain.atlassian.net
export JIRA_API_TOKEN=your_token
# or
export NOTION_API_KEY=secret_your_key

# 2. Run the server
cd github-mcp
python server.py
```

Server starts on `http://localhost:8080` with metrics at `:9090/metrics`

---

## 🏗️ Architecture Pattern

All examples follow the same architecture:

```
┌──────────────────┐
│  LLM Application │  (Claude, GPT-4, etc.)
└────────┬─────────┘
         │ MCP Protocol
         ↓
┌────────────────────────────────┐
│  Enterprise MCP Framework      │
│  ┌──────────────────────────┐  │
│  │  Security                │  │  ← OAuth, RBAC, Encryption
│  ├──────────────────────────┤  │
│  │  Observability           │  │  ← Metrics, Tracing, Logs
│  ├──────────────────────────┤  │
│  │  Governance              │  │  ← Approvals, Audit, Compliance
│  ├──────────────────────────┤  │
│  │  Cost Management         │  │  ← Rate Limits, Budgets
│  └──────────────────────────┘  │
└────────┬───────────────────────┘
         │ API Calls
         ↓
┌────────────────────┐
│  External Service  │  (GitHub, Jira, Notion)
└────────────────────┘
```

---

## 📊 Comparison

| Example | API Calls/Month | Cost/Month | Approval Workflows | Compliance |
|---------|----------------|------------|-------------------|------------|
| **GitHub** | 50K | $0 (free tier) | PRs to main | SOC2 |
| **Jira** | 100K | $120 | Ticket transitions | SOX |
| **Notion** | 30K | $80 | Page deletion | GDPR |

---

## 🔒 Security Best Practices

### 1. Credential Management
```bash
# ✅ Use environment variables
export GITHUB_TOKEN=ghp_xxx

# ✅ Or use secrets manager
aws secretsmanager get-secret-value --secret-id github-token

# ❌ Never hardcode tokens
# token = "ghp_xxx"  # DON'T DO THIS
```

### 2. RBAC Configuration
```yaml
security:
  rbac:
    enabled: true
    default_role: viewer  # Principle of least privilege
    roles:
      viewer: [read]
      editor: [read, write]
      admin: ["*"]
```

### 3. Audit Logging
```yaml
governance:
  audit:
    enabled: true
    storage: postgresql
    retention_days: 2555  # SOX: 7 years
    pii_masking: true     # GDPR compliance
```

---

## 📈 Monitoring

### Metrics to Watch

**Request Metrics**:
```
mcp_requests_total{server="github-mcp", operation="create_issue"}
mcp_request_duration_seconds{server="github-mcp", operation="search_code"}
mcp_errors_total{server="github-mcp", error_type="rate_limit"}
```

**Cost Metrics**:
```
mcp_api_calls_total{server="jira-mcp", user="alice"}
mcp_cost_usd{server="jira-mcp", team="engineering"}
```

**Governance Metrics**:
```
mcp_approvals_pending{server="github-mcp", operation="create_pr"}
mcp_audit_logs_total{server="jira-mcp"}
```

### Grafana Dashboards

Pre-built dashboards for each example:
- **Overview**: Request rates, errors, latency
- **Security**: Auth attempts, RBAC decisions
- **Cost**: API usage, budget vs actual
- **Governance**: Approval workflows, audit trails

---

## 🛠️ Customization

### Add Custom Operations

```python
# Add to server.py
def custom_operation(self, params):
    """Your custom operation."""
    # Implementation
    return result

# Register with Enterprise MCP
proxy.register_operation("custom_operation", custom_operation)
```

### Add Custom Approval Rules

```yaml
# config.yaml
governance:
  approvals:
    - name: high_risk_operations
      conditions:
        operations: ["delete_*", "terminate_*"]
        cost_threshold: 1000  # USD
      approvers:
        - slack: "#approvals"
        - email: "ops-team@company.com"
      required_approvals: 2
      timeout: 3600  # 1 hour
```

### Add Custom Metrics

```python
# In server.py
from prometheus_client import Counter

custom_metric = Counter(
    'mcp_custom_operations_total',
    'Custom operations counter',
    ['server', 'operation']
)

custom_metric.labels(server='github-mcp', operation='custom').inc()
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Rate Limit Errors**
```
Error: API rate limit exceeded
Solution: Check rate limit status, increase limits, or implement caching
```

**2. Permission Denied**
```
Error: 403 Forbidden - User lacks required permission
Solution: Grant user the required RBAC role via config.yaml
```

**3. Approval Timeout**
```
Error: Approval request timed out after 1 hour
Solution: Notify approvers, adjust timeout, or add backup approvers
```

---

## 📝 Contributing

Want to add more examples?

1. Create new directory: `examples/your-service-mcp/`
2. Implement MCP server: `server.py`
3. Add enterprise features: RBAC, approvals, audit logs
4. Write documentation: `README.md`
5. Add tests: `tests/`
6. Submit PR

**Most wanted examples**:
- Slack MCP (messaging, channel management)
- AWS MCP (EC2, S3, Lambda operations)
- PostgreSQL MCP (database queries with SOX compliance)
- Salesforce MCP (CRM operations)

---

## 📄 License

MIT License - see [LICENSE](../LICENSE)

---

**Built with ❤️ using Enterprise MCP Framework**

*Make any MCP server enterprise-ready in minutes.*
