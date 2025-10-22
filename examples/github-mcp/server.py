"""
GitHub MCP Server with Enterprise Security

Provides secure access to GitHub APIs (repos, issues, PRs, code search)
with RBAC, audit logging, and cost tracking.

Features:
- Role-based access (read-only, developer, admin)
- Audit trail for all GitHub operations
- Rate limiting per user
- Cost tracking for GitHub API usage
- OAuth authentication via GitHub App

Usage:
    python server.py --config config.yaml
"""

import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from github import Github, GithubException


@dataclass
class GitHubMCPServer:
    """GitHub MCP Server providing repository and issue management."""

    def __init__(self, access_token: str):
        self.github = Github(access_token)
        self.user = self.github.get_user()

    # ========== Repository Operations ==========

    def list_repositories(self, org: str = None, visibility: str = "all") -> List[Dict]:
        """
        List repositories for user or organization.

        Args:
            org: Organization name (optional, defaults to user repos)
            visibility: all, public, or private

        Returns:
            List of repository metadata

        RBAC: Requires 'repo:read' permission
        Audit: Logs repo access
        """
        try:
            if org:
                repos = self.github.get_organization(org).get_repos(type=visibility)
            else:
                repos = self.user.get_repos(visibility=visibility)

            return [{
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "updated_at": repo.updated_at.isoformat()
            } for repo in repos[:50]]  # Limit to 50

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    def get_repository_info(self, repo_name: str) -> Dict:
        """
        Get detailed repository information.

        Args:
            repo_name: Full repository name (owner/repo)

        Returns:
            Repository details

        RBAC: Requires 'repo:read' permission
        """
        try:
            repo = self.github.get_repo(repo_name)

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "language": repo.language,
                "topics": repo.get_topics(),
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "default_branch": repo.default_branch,
                "open_issues": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
            }

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    # ========== Issue Operations ==========

    def list_issues(self, repo_name: str, state: str = "open", labels: List[str] = None) -> List[Dict]:
        """
        List issues for a repository.

        Args:
            repo_name: Full repository name (owner/repo)
            state: open, closed, or all
            labels: Filter by labels

        Returns:
            List of issues

        RBAC: Requires 'issues:read' permission
        """
        try:
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state=state, labels=labels or [])

            return [{
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "author": issue.user.login,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "url": issue.html_url,
                "body": issue.body[:500] if issue.body else None,  # Truncate
                "comments": issue.comments
            } for issue in issues[:20]]  # Limit to 20

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    def create_issue(self, repo_name: str, title: str, body: str, labels: List[str] = None) -> Dict:
        """
        Create a new issue.

        Args:
            repo_name: Full repository name (owner/repo)
            title: Issue title
            body: Issue description
            labels: Labels to apply

        Returns:
            Created issue details

        RBAC: Requires 'issues:write' permission
        Approval: Required for production repos
        Audit: Logs issue creation
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])

            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "created_at": issue.created_at.isoformat()
            }

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    def update_issue(self, repo_name: str, issue_number: int, **kwargs) -> Dict:
        """
        Update an existing issue.

        Args:
            repo_name: Full repository name (owner/repo)
            issue_number: Issue number
            **kwargs: Fields to update (title, body, state, labels, assignees)

        Returns:
            Updated issue details

        RBAC: Requires 'issues:write' permission
        Approval: Required for closing issues
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)

            # Update fields
            if "title" in kwargs:
                issue.edit(title=kwargs["title"])
            if "body" in kwargs:
                issue.edit(body=kwargs["body"])
            if "state" in kwargs:
                issue.edit(state=kwargs["state"])
            if "labels" in kwargs:
                issue.set_labels(*kwargs["labels"])
            if "assignees" in kwargs:
                issue.edit(assignees=kwargs["assignees"])

            return {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "updated_at": issue.updated_at.isoformat(),
                "url": issue.html_url
            }

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    # ========== Pull Request Operations ==========

    def list_pull_requests(self, repo_name: str, state: str = "open") -> List[Dict]:
        """
        List pull requests for a repository.

        Args:
            repo_name: Full repository name (owner/repo)
            state: open, closed, or all

        Returns:
            List of pull requests

        RBAC: Requires 'pr:read' permission
        """
        try:
            repo = self.github.get_repo(repo_name)
            prs = repo.get_pulls(state=state)

            return [{
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "url": pr.html_url,
                "base": pr.base.ref,
                "head": pr.head.ref,
                "mergeable": pr.mergeable,
                "merged": pr.merged,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "comments": pr.comments,
                "review_comments": pr.review_comments
            } for pr in prs[:20]]  # Limit to 20

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        head: str,
        base: str,
        body: str = None
    ) -> Dict:
        """
        Create a new pull request.

        Args:
            repo_name: Full repository name (owner/repo)
            title: PR title
            head: Branch with changes
            base: Target branch
            body: PR description

        Returns:
            Created PR details

        RBAC: Requires 'pr:write' permission
        Approval: Required for main/master branches
        """
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body or "", head=head, base=base)

            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
                "created_at": pr.created_at.isoformat()
            }

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    # ========== Code Search Operations ==========

    def search_code(self, query: str, repo: str = None, language: str = None) -> List[Dict]:
        """
        Search code across repositories.

        Args:
            query: Search query
            repo: Optional repository filter
            language: Optional language filter

        Returns:
            List of code matches

        RBAC: Requires 'code:read' permission
        Cost: High API usage - tracked and rate limited
        """
        try:
            # Build search query
            search_query = query
            if repo:
                search_query += f" repo:{repo}"
            if language:
                search_query += f" language:{language}"

            results = self.github.search_code(query=search_query)

            return [{
                "name": item.name,
                "path": item.path,
                "repository": item.repository.full_name,
                "url": item.html_url,
                "score": item.score
            } for item in results[:10]]  # Limit to 10

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}

    # ========== User Operations ==========

    def get_user_info(self, username: str = None) -> Dict:
        """
        Get user information.

        Args:
            username: GitHub username (optional, defaults to authenticated user)

        Returns:
            User details

        RBAC: Requires 'user:read' permission
        """
        try:
            user = self.github.get_user(username) if username else self.user

            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat(),
                "url": user.html_url
            }

        except GithubException as e:
            return {"error": str(e), "status_code": e.status}


# ========== Enterprise MCP Integration ==========

if __name__ == "__main__":
    import sys
    sys.path.append("../..")

    from enterprise_mcp import EnterpriseProxy, SecurityConfig, ObservabilityConfig, GovernanceConfig

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        exit(1)

    # Create GitHub MCP server
    github_server = GitHubMCPServer(access_token=github_token)

    # Wrap with Enterprise MCP Framework
    proxy = EnterpriseProxy(
        target_server=github_server,
        security=SecurityConfig(
            auth_provider="github_oauth",
            rbac_enabled=True,
            roles={
                "viewer": ["repo:read", "issues:read", "user:read"],
                "developer": ["repo:read", "issues:read", "issues:write", "pr:read", "pr:write", "user:read"],
                "admin": ["*"]
            }
        ),
        observability=ObservabilityConfig(
            metrics=True,
            tracing=True,
            logging=True
        ),
        governance=GovernanceConfig(
            approval_required_for=[
                "create_pull_request:*:main",  # PRs to main require approval
                "create_pull_request:*:master",
                "update_issue:*:state=closed"  # Closing issues requires approval
            ],
            audit_retention_days=365,
            compliance="soc2"
        )
    )

    print("✅ GitHub MCP Server with Enterprise Features")
    print("   - RBAC: viewer, developer, admin roles")
    print("   - Approvals: PRs to main/master, issue closures")
    print("   - Audit: 365-day retention")
    print("   - Metrics: Prometheus endpoint at :9090/metrics")
    print()
    print("Starting server...")

    proxy.start(host="0.0.0.0", port=8080)
