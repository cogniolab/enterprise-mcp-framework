# Jira MCP Server Example

Enterprise-ready Jira integration for ticket management, sprint planning, and reporting.

## Features

✅ **Issue Management** - Create, update, search, transition tickets
✅ **Sprint Planning** - Query sprints, backlogs, velocity
✅ **Project Management** - List projects, components, versions
✅ **Reporting** - Burndown charts, velocity, SLA compliance
✅ **JQL Search** - Advanced Jira Query Language support

## Enterprise Features

🔒 **Security**: OAuth 2.0, RBAC (viewer/contributor/admin)
📊 **Observability**: Real-time ticket metrics, SLA tracking
⚖️ **Governance**: Approvals for status transitions, SOX compliance
💰 **Cost**: API usage tracking, budget alerts

## Quick Start

```bash
pip install jira enterprise-mcp-framework
export JIRA_URL=https://your-domain.atlassian.net
export JIRA_API_TOKEN=your_token
python server.py
```

## Example Operations

### Create Ticket (with Approval)
```python
mcp_client.call(
    server="jira-mcp",
    method="create_issue",
    params={
        "project": "PROJ",
        "summary": "Bug in login flow",
        "issue_type": "Bug",
        "priority": "High",
        "description": "Detailed description..."
    }
)
# Returns: {"key": "PROJ-123", "status": "pending_approval"}
```

### Transition Ticket (Requires Approval for Production)
```python
mcp_client.call(
    server="jira-mcp",
    method="transition_issue",
    params={
        "issue_key": "PROJ-123",
        "transition": "Done",
        "comment": "Fixed and deployed"
    }
)
# Production tickets require PM approval before "Done"
```

### JQL Search
```python
mcp_client.call(
    server="jira-mcp",
    method="search_issues",
    params={
        "jql": "project = PROJ AND status = 'In Progress' AND assignee = currentUser()",
        "max_results": 50
    }
)
```

## RBAC Roles

- **Viewer**: Read-only access to tickets and reports
- **Contributor**: Create/update tickets, comment, assign
- **Project Lead**: Manage sprints, components, versions
- **Admin**: All permissions, system configuration

## Approval Workflows

- **Closing production tickets**: Requires PM approval
- **Changing sprint scope**: Requires team lead approval
- **Deleting tickets**: Requires admin approval (SOX compliance)

## Metrics

```
mcp_jira_tickets_created_total{project="PROJ", type="Bug"} 142
mcp_jira_sla_breaches_total{project="PROJ", severity="high"} 3
mcp_jira_cycle_time_seconds{project="PROJ", type="Story"} 172800  # 2 days
```

## Audit Trail (SOX Compliance)

All Jira operations logged with 7-year retention:
- Who created/modified tickets
- Status transitions with timestamps
- Custom field changes
- Approval decisions

## Use Cases

1. **AI Ticket Triage**: Auto-label and route tickets
2. **Sprint Planning Assistant**: Analyze velocity, suggest story points
3. **SLA Monitoring**: Alert on SLA breaches
4. **Release Planning**: Track epics, dependencies, blockers

---

**See `server.py` for full implementation**
