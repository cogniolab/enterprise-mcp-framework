# GitHub MCP Server Example

Enterprise-ready GitHub integration with RBAC, audit logging, and approvals.

## Features

✅ **Repository Management** - List, search, and query repos
✅ **Issue Tracking** - Create, update, search issues
✅ **Pull Requests** - Manage PRs with approval workflows
✅ **Code Search** - Semantic code search with rate limiting
✅ **User Management** - Query user and org information

## Enterprise Features

🔒 **Security**: GitHub OAuth, RBAC (viewer/developer/admin roles)
📊 **Observability**: Prometheus metrics, OpenTelemetry tracing
⚖️ **Governance**: Approvals for PRs to main, issue closures
💰 **Cost**: Rate limiting on expensive operations (code search)

## Quick Start

### 1. Install Dependencies

```bash
pip install PyGithub enterprise-mcp-framework
```

### 2. Set GitHub Token

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### 3. Run Server

```bash
python server.py
```

Server starts on `http://localhost:8080` with metrics at `:9090/metrics`

## Usage Examples

### List Repositories

```python
# Via MCP client
response = mcp_client.call(
    server="github-mcp",
    method="list_repositories",
    params={"org": "anthropics", "visibility": "public"}
)
```

### Create Issue (Requires Approval)

```python
# Create issue (auto-logged, requires developer role)
response = mcp_client.call(
    server="github-mcp",
    method="create_issue",
    params={
        "repo_name": "cogniolab/enterprise-mcp-framework",
        "title": "Add new feature",
        "body": "Detailed description...",
        "labels": ["enhancement"]
    }
)
# Returns: {"status": "pending_approval", "approval_id": "..."}
```

### Search Code (Rate Limited)

```python
# Code search (high cost operation - rate limited per user)
response = mcp_client.call(
    server="github-mcp",
    method="search_code",
    params={
        "query": "def train_model",
        "language": "python"
    }
)
```

## RBAC Roles

### Viewer
- `repo:read` - List and view repositories
- `issues:read` - View issues and PRs
- `user:read` - View user information

### Developer
- All viewer permissions
- `issues:write` - Create and update issues
- `pr:write` - Create and update PRs

### Admin
- All permissions (`*`)
- Bypass approval workflows
- Access sensitive operations

## Approval Workflows

Operations requiring approval:
- **PRs to main/master** - 1 approval from team lead
- **Issue closures** - 1 approval from product manager
- **Repository deletions** - 2 approvals from admins

Approvers notified via:
- Slack: `#eng-approvals` channel
- Email: eng-team@company.com

## Metrics

### Request Metrics
```
mcp_requests_total{server="github-mcp", operation="create_issue"} 142
mcp_request_duration_seconds{server="github-mcp", operation="list_repositories"} 0.234
```

### Cost Metrics
```
mcp_github_api_calls_total{user="alice", operation="search_code"} 45
mcp_github_rate_limit_remaining{user="alice"} 4955
```

### Governance Metrics
```
mcp_approvals_pending{operation="create_pull_request"} 3
mcp_approvals_approved{operation="create_pull_request"} 127
```

## Audit Trail

All GitHub operations logged:

```json
{
  "timestamp": "2025-10-22T07:50:00Z",
  "user": "alice@company.com",
  "operation": "create_issue",
  "server": "github-mcp",
  "params": {
    "repo_name": "cogniolab/enterprise-mcp-framework",
    "title": "Add documentation"
  },
  "result": "success",
  "duration_ms": 234,
  "ip_address": "10.0.1.45",
  "approval_required": false
}
```

## Configuration

```yaml
# config/github-mcp.yaml
server:
  name: github-mcp
  port: 8080

security:
  auth:
    provider: github_oauth
    client_id: ${GITHUB_CLIENT_ID}
    client_secret: ${GITHUB_CLIENT_SECRET}

  rbac:
    enabled: true
    roles:
      viewer:
        - repo:read
        - issues:read
      developer:
        - repo:read
        - issues:write
        - pr:write
      admin:
        - "*"

governance:
  approvals:
    - operations:
        - create_pull_request:*:main
        - create_pull_request:*:master
      approvers:
        - slack: "#eng-leads"
      required: 1

    - operations:
        - update_issue:*:state=closed
      approvers:
        - slack: "#product-team"
      required: 1

cost_management:
  rate_limits:
    search_code:
      per_user: 100/hour
      per_team: 500/hour

  budgets:
    api_calls_per_month: 50000
    alert_threshold: 0.8

observability:
  metrics:
    enabled: true
    port: 9090
  tracing:
    enabled: true
    endpoint: http://jaeger:14268/api/traces
  logging:
    level: info
    format: json
```

## Deployment

### Docker

```bash
docker build -t github-mcp .
docker run -d \
  -p 8080:8080 \
  -p 9090:9090 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  github-mcp
```

### Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl expose deployment github-mcp --type=LoadBalancer --port=8080
```

## Troubleshooting

### Rate Limit Errors

```python
# Error: GitHub API rate limit exceeded
# Solution: Check current limits
mcp_client.call(server="github-mcp", method="get_rate_limit")
# Wait or use authenticated requests (higher limits)
```

### Permission Denied

```python
# Error: 403 Forbidden
# Solution: Check RBAC role has required permission
# Contact admin to grant 'issues:write' permission
```

## Security Best Practices

✅ Use fine-grained personal access tokens (not classic tokens)
✅ Rotate tokens every 90 days
✅ Enable GitHub App authentication for production
✅ Use separate tokens for dev/staging/prod
✅ Never commit tokens to git (use secrets manager)

## Cost Optimization

GitHub API limits:
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour
- **GitHub App**: 15,000 requests/hour

**Recommendation**: Use GitHub App authentication for 3x higher limits.

## Use Cases

### 1. Automated Issue Triage
AI agent reads new issues, labels them, assigns to team members.

### 2. PR Review Assistant
AI agent reviews PRs for common issues, suggests improvements.

### 3. Code Search for Documentation
AI agent searches codebase to answer developer questions.

### 4. Release Notes Generation
AI agent summarizes PRs and commits for release notes.

## Next Steps

1. **Enable GitHub App**: Higher rate limits, better security
2. **Add Webhooks**: Real-time notifications for events
3. **Custom Metrics**: Track team velocity, PR cycle time
4. **Integration**: Connect with Jira, Slack, PagerDuty

---

**Built with ❤️ using Enterprise MCP Framework**
