# Contributing to Enterprise MCP Framework

Thank you for interest in contributing to the Enterprise MCP Framework. This document provides guidelines to ensure high-quality contributions aligned with our production standards.

## Getting Started

1. **Fork and Clone**
   ```
   git clone https://github.com/yourusername/enterprise-mcp-framework.git
   cd enterprise-mcp-framework
   ```

2. **Set Up Development Environment**
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   make setup
   ```

## Contribution Types

### Bug Reports
- Use GitHub Issues with template
- Include reproduction steps and environment details
- Attach relevant logs and error traces

### Features
- Open a Discussion first for major changes
- Submit RFC (Request for Comments) for architectural changes
- Include security and performance implications

### Documentation
- Update README, API docs, and inline comments
- Add examples for new features
- Verify links and code snippets work

## Code Standards

### Security Requirements
- No hardcoded credentials or secrets
- Run `make security-check` before submission
- Include security considerations in PRs
- Add tests for authentication/authorization paths

### Quality Checklist
- Write tests: minimum 80% coverage
- Run `make lint` and fix issues
- Update CHANGELOG.md
- Follow PEP 8 style guide
- Add type hints (Python 3.10+)

### Example Contribution
```python
# Good: Clear docstring, type hints, error handling
def validate_policy(policy: Dict[str, Any]) -> bool:
    """Validate governance policy structure.
    
    Args:
        policy: Policy configuration dictionary
        
    Returns:
        True if valid, raises ValidationError otherwise
        
    Security: Validates policy doesn't enable unauthorized access
    """
    if not policy.get("version"):
        raise ValidationError("Missing policy version")
    return True
```

## Pull Request Process

1. **Branch Naming**: `feature/description` or `fix/description`
2. **Commit Messages**: Follow conventional commits
   - `feat(security): add RBAC validation`
   - `fix(observability): resolve metric race condition`
3. **PR Template**: Use provided template
4. **Reviews**: At least 2 maintainer approvals for production changes
5. **Tests**: All CI checks must pass

## Testing

```bash
make test                    # Run all tests
make test-coverage          # Generate coverage report
make test-security          # Run security checks
make test-performance       # Run benchmarks
```

## Documentation

- Add docstrings following Google style
- Update examples/ directory for new features
- Include diagrams for architecture changes
- Update API documentation in docs/

## Community Guidelines

- Be respectful and inclusive
- Assume good intentions
- Provide constructive feedback
- Help others learn

## Review Criteria

We prioritize contributions that:
- Maintain or improve security posture
- Don't degrade performance
- Include comprehensive tests
- Follow established patterns
- Include documentation

## Questions?

- Check existing issues and discussions
- Review documentation in docs/
- Join our community Slack (link in README)

---

**Code of Conduct**: We enforce our Code of Conduct strictly. Report violations to security@yourdomain.com

**License**: All contributions are licensed under Apache 2.0