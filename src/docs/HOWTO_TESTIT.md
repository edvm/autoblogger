# AutoBlogger Backend Testing Guide

This guide provides comprehensive instructions for running tests in the AutoBlogger backend project, with special focus on the new API key authentication system.

## Table of Contents

- [Quick Start](#quick-start)
- [Testing Overview](#testing-overview)
- [Test Categories](#test-categories)
- [Basic Commands](#basic-commands)
- [Authentication System Testing](#authentication-system-testing)
- [Advanced Testing](#advanced-testing)
- [Coverage and Reporting](#coverage-and-reporting)
- [CI/CD Integration](#cicd-integration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Quick Start

### Essential Commands

```bash
# Run all tests
uv run pytest

# Run authentication tests only
uv run pytest tests/test_*auth* -v

# Run with coverage
uv run pytest --cov=api --cov-report=html

# Run specific test file
uv run pytest tests/test_system_auth_models.py -v

# Stop on first failure
uv run pytest -x
```

### Most Common Developer Workflows

```bash
# Test what you're working on
uv run pytest tests/test_system_auth_endpoints.py::TestSystemUserRegistration -v

# Quick security check
uv run pytest tests/test_auth_security.py -v

# Full authentication test suite
uv run pytest tests/test_*auth* --cov=api.auth_strategies --cov=api.database
```

## Testing Overview

### Framework and Tools

- **Testing Framework**: pytest 8.4.0+ with async support
- **Coverage**: pytest-cov with HTML reporting
- **Mocking**: pytest-mock for test isolation
- **Database**: SQLite in-memory for test isolation
- **Async Support**: pytest-asyncio for async authentication methods

### Test Architecture

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── utils/
│   └── auth_test_utils.py          # Authentication test utilities
├── test_system_auth_models.py      # Database model unit tests
├── test_auth_strategies.py         # Authentication strategy tests
├── test_system_auth_endpoints.py   # API endpoint integration tests
├── test_auth_security.py           # Security and vulnerability tests
└── test_api_endpoints.py           # Existing API tests
```

### Coverage Goals

- **Overall Coverage**: 50%+ (currently achieving 51%)
- **Authentication Code**: 90%+ coverage required
- **Security Critical**: 100% coverage for security functions
- **New Features**: 80%+ coverage for new authentication system

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

```bash
# Database model tests
uv run pytest tests/test_system_auth_models.py -m unit -v

# Authentication strategy tests
uv run pytest tests/test_auth_strategies.py -m unit -v
```

### Integration Tests (`@pytest.mark.integration`)

Test component interactions:

```bash
# API endpoint tests
uv run pytest tests/test_system_auth_endpoints.py -m integration -v

# Full system integration
uv run pytest -m integration
```

### Security Tests (`@pytest.mark.security`)

Test security vulnerabilities and attack vectors:

```bash
# Security-focused tests
uv run pytest tests/test_auth_security.py -m security -v

# All security tests
uv run pytest -m security
```

### Authentication Tests (`@pytest.mark.auth`)

Test authentication flows and security:

```bash
# All authentication tests
uv run pytest -m auth -v

# Authentication and security combined
uv run pytest -m "auth or security"
```

## Basic Commands

### Running Tests

```bash
# Run all tests (full suite)
uv run pytest

# Run with verbose output
uv run pytest -v

# Run very verbose (show test parameters)
uv run pytest -vv

# Run quietly (minimal output)
uv run pytest -q

# Stop on first failure
uv run pytest -x

# Run specific number of failures before stopping
uv run pytest --maxfail=3
```

### Test Selection

```bash
# Run specific test file
uv run pytest tests/test_system_auth_models.py

# Run specific test class
uv run pytest tests/test_system_auth_models.py::TestSystemUser

# Run specific test method
uv run pytest tests/test_auth_security.py::TestPasswordSecurity::test_password_hashing_uses_bcrypt

# Run tests matching pattern
uv run pytest -k "test_password" -v

# Run tests by marker
uv run pytest -m "unit and not slow"
```

### Output Control

```bash
# Show local variables on failure
uv run pytest -l

# Show test durations (slowest first)
uv run pytest --durations=10

# Show test durations for all tests
uv run pytest --durations=0

# Capture stdout/stderr
uv run pytest -s

# Show warnings
uv run pytest -W ignore::DeprecationWarning
```

## Authentication System Testing

### Database Model Tests

```bash
# Test SystemUser model
uv run pytest tests/test_system_auth_models.py::TestSystemUser -v

# Test API key functionality
uv run pytest tests/test_system_auth_models.py::TestApiKey -v

# Test User model updates
uv run pytest tests/test_system_auth_models.py::TestUser -v

# Test model relationships
uv run pytest tests/test_system_auth_models.py::TestModelIntegration -v
```

### Authentication Strategy Tests

```bash
# Test API key authentication
uv run pytest tests/test_auth_strategies.py::TestApiKeyAuthStrategy -v

# Test Clerk authentication (backward compatibility)
uv run pytest tests/test_auth_strategies.py::TestClerkAuthStrategy -v

# Test authentication manager
uv run pytest tests/test_auth_strategies.py::TestAuthStrategyManager -v

# Test all authentication strategies
uv run pytest tests/test_auth_strategies.py -v
```

### API Endpoint Tests

```bash
# Test user registration
uv run pytest tests/test_system_auth_endpoints.py::TestSystemUserRegistration -v

# Test user login
uv run pytest tests/test_system_auth_endpoints.py::TestSystemUserLogin -v

# Test API key management
uv run pytest tests/test_system_auth_endpoints.py::TestApiKeyManagement -v

# Test current user endpoints
uv run pytest tests/test_system_auth_endpoints.py::TestCurrentUserEndpoints -v

# Test endpoint security
uv run pytest tests/test_system_auth_endpoints.py::TestAuthenticationEndpointsSecurity -v
```

### Security Tests

```bash
# Test password security
uv run pytest tests/test_auth_security.py::TestPasswordSecurity -v

# Test API key security
uv run pytest tests/test_auth_security.py::TestApiKeySecurity -v

# Test authentication bypass prevention
uv run pytest tests/test_auth_security.py::TestAuthenticationBypass -v

# Test input validation security
uv run pytest tests/test_auth_security.py::TestInputValidationSecurity -v

# Test brute force protection
uv run pytest tests/test_auth_security.py::TestBruteForceProtection -v
```

### Mixed Authentication Testing

```bash
# Test both authentication methods
uv run pytest tests/test_*auth* -k "clerk or system" -v

# Test backward compatibility
uv run pytest tests/test_auth_strategies.py::TestClerkAuthStrategy -v

# Test authentication strategy manager
uv run pytest tests/test_auth_strategies.py::TestAuthStrategyManager -v
```

## Advanced Testing

### Parallel Test Execution

```bash
# Install pytest-xdist for parallel execution
uv add pytest-xdist

# Run tests in parallel
uv run pytest -n auto

# Run with specific number of processes
uv run pytest -n 4

# Run authentication tests in parallel
uv run pytest tests/test_*auth* -n 2
```

### Test Data and Fixtures

```bash
# Run tests with custom test data
uv run pytest tests/test_system_auth_endpoints.py --tb=short

# Debug test fixtures
uv run pytest tests/test_system_auth_models.py -s --setup-show

# Run with specific database
DATABASE_URL=sqlite:///:memory: uv run pytest tests/test_system_auth_models.py
```

### Async Testing

```bash
# Run async authentication tests
uv run pytest tests/test_auth_strategies.py -v --asyncio-mode=auto

# Test async authentication strategies
uv run pytest tests/test_auth_strategies.py::TestApiKeyAuthStrategy::test_authenticate_success
```

### Performance Testing

```bash
# Run with performance profiling
uv run pytest tests/test_auth_security.py::TestApiKeySecurity::test_api_key_generation_entropy --profile

# Benchmark authentication performance
uv run pytest tests/test_auth_security.py -k "performance" --benchmark-only
```

## Coverage and Reporting

### Basic Coverage

```bash
# Run with coverage
uv run pytest --cov=api

# Coverage with missing lines
uv run pytest --cov=api --cov-report=term-missing

# Coverage for specific modules
uv run pytest --cov=api.auth_strategies --cov=api.database
```

### HTML Coverage Reports

```bash
# Generate HTML coverage report
uv run pytest --cov=api --cov-report=html

# Open coverage report (macOS)
open htmlcov/index.html

# Open coverage report (Linux)
xdg-open htmlcov/index.html
```

### Coverage for Authentication System

```bash
# Authentication module coverage
uv run pytest tests/test_*auth* --cov=api.auth_strategies --cov=api.database --cov=api.routers.system_auth --cov-report=html

# Security test coverage
uv run pytest tests/test_auth_security.py --cov=api --cov-report=term-missing

# Database model coverage
uv run pytest tests/test_system_auth_models.py --cov=api.database --cov-report=term-missing
```

### XML Coverage (for CI/CD)

```bash
# Generate XML coverage for CI
uv run pytest --cov=api --cov-report=xml

# Generate both HTML and XML
uv run pytest --cov=api --cov-report=html --cov-report=xml
```

## CI/CD Integration

### GitHub Actions

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          uv run pytest tests/test_*auth* --cov=api --cov-report=xml
          uv run pytest --cov=api --cov-fail-under=30
```

### Pre-commit Testing

```bash
# Run authentication tests before commit
uv run pytest tests/test_*auth* -x

# Run security tests before commit
uv run pytest tests/test_auth_security.py -x

# Run fast tests only
uv run pytest -m "not slow" -x
```

### Continuous Integration Commands

```bash
# Full CI test suite
uv run pytest --cov=api --cov-report=xml --cov-fail-under=30

# Security-focused CI
uv run pytest tests/test_auth_security.py --cov=api --cov-fail-under=50

# Performance regression testing
uv run pytest tests/test_auth_security.py -k "performance" --benchmark-json=benchmark.json
```

## Development Workflow

### Test-Driven Development

```bash
# 1. Write failing test
uv run pytest tests/test_system_auth_models.py::TestSystemUser::test_new_feature -v

# 2. Run specific test during development
uv run pytest tests/test_system_auth_models.py::TestSystemUser::test_new_feature -v -s

# 3. Run related tests
uv run pytest tests/test_system_auth_models.py::TestSystemUser -v

# 4. Run full test suite
uv run pytest tests/test_*auth* -v
```

### Debugging Tests

```bash
# Debug specific failing test
uv run pytest tests/test_auth_strategies.py::TestApiKeyAuthStrategy::test_authenticate_success -v -s --tb=long

# Run with Python debugger
uv run pytest tests/test_system_auth_models.py::TestSystemUser::test_password_hashing_uses_bcrypt --pdb

# Show local variables on failure
uv run pytest tests/test_auth_security.py -l -v
```

### Test File Organization

```bash
# Test specific component
uv run pytest tests/test_system_auth_models.py::TestApiKey -v

# Test related functionality
uv run pytest tests/test_*auth* -k "api_key" -v

# Test by category
uv run pytest tests/test_auth_security.py::TestPasswordSecurity -v
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: ModuleNotFoundError
# Solution: Install dependencies
uv sync

# Error: Cannot import from api.auth_strategies
# Solution: Check Python path
PYTHONPATH=/path/to/backend uv run pytest
```

#### 2. Database Issues

```bash
# Error: Database connection issues
# Solution: Use in-memory database
DATABASE_URL=sqlite:///:memory: uv run pytest tests/test_system_auth_models.py

# Error: Table doesn't exist
# Solution: Initialize test database
uv run pytest tests/test_system_auth_models.py::TestModelIntegration::test_system_user_api_key_relationship -v
```

#### 3. Async Test Issues

```bash
# Error: async function not properly tested
# Solution: Use pytest-asyncio
uv run pytest tests/test_auth_strategies.py -v --asyncio-mode=auto

# Error: Event loop issues
# Solution: Install pytest-asyncio
uv add pytest-asyncio
```

#### 4. Mock and Fixture Issues

```bash
# Error: Mock not working
# Solution: Debug with verbose output
uv run pytest tests/test_system_auth_endpoints.py -v -s

# Error: Fixture not found
# Solution: Check conftest.py
uv run pytest tests/test_system_auth_models.py --fixtures
```

### Environment Issues

```bash
# Check test environment
uv run pytest --collect-only tests/test_*auth*

# Check test configuration
uv run pytest --help | grep -A5 -B5 "markers"

# Debug test discovery
uv run pytest tests/test_system_auth_models.py --collect-only -q
```

### Performance Issues

```bash
# Find slow tests
uv run pytest tests/test_*auth* --durations=10

# Run only fast tests
uv run pytest -m "not slow" tests/test_*auth*

# Profile specific test
uv run pytest tests/test_auth_security.py::TestApiKeySecurity::test_api_key_generation_entropy --profile
```

## Best Practices

### Test Organization

```bash
# Group related tests
uv run pytest tests/test_system_auth_models.py::TestSystemUser -v

# Use descriptive test names
uv run pytest -k "test_password_hashing" -v

# Test edge cases
uv run pytest tests/test_auth_security.py -v
```

### Development Guidelines

```bash
# Always run tests before commit
uv run pytest tests/test_*auth* -x

# Run security tests for auth changes
uv run pytest tests/test_auth_security.py -v

# Verify backward compatibility
uv run pytest tests/test_auth_strategies.py::TestClerkAuthStrategy -v
```

### Performance Considerations

```bash
# Use parallel execution for large test suites
uv run pytest -n auto tests/test_*auth*

# Run unit tests separately from integration tests
uv run pytest -m unit tests/test_*auth*
uv run pytest -m integration tests/test_*auth*
```

### Code Quality

```bash
# Run linting alongside tests
uv run ruff check . && uv run pytest tests/test_*auth*

# Format code before testing
uv run ruff format . && uv run pytest tests/test_*auth*

# Type checking with tests
uv run mypy api/ && uv run pytest tests/test_*auth*
```

## Test Configuration

### Environment Variables

```bash
# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite:///:memory:

# Test with different LLM providers
LLM_PROVIDER=openai uv run pytest tests/test_*auth*
LLM_PROVIDER=gemini uv run pytest tests/test_*auth*
```

### Configuration Files

- **`pyproject.toml`**: Main test configuration
- **`pytest.ini`**: Legacy pytest configuration (if exists)
- **`conftest.py`**: Shared fixtures and setup
- **`.env.test`**: Test environment variables (if exists)

### Markers Configuration

```bash
# List available markers
uv run pytest --markers

# Run tests by custom markers
uv run pytest -m "auth and not slow"
uv run pytest -m "security or integration"
```

## Need Help?

1. **Check Test Output**: Use `-v` flag for verbose output
2. **Debug with Print**: Use `-s` flag to see print statements
3. **Check Coverage**: Use `--cov-report=html` for detailed coverage
4. **Review Fixtures**: Check `conftest.py` for available fixtures
5. **Validate Environment**: Ensure all dependencies are installed with `uv sync`

For additional support, refer to the [setup guide](HOWTO_SETUP.md) or check the test files for examples of proper usage patterns.

## Quick Reference

### Most Used Commands
```bash
# Quick test run
uv run pytest tests/test_*auth* -v

# Coverage report
uv run pytest --cov=api --cov-report=html

# Security check
uv run pytest tests/test_auth_security.py -v

# Debug failing test
uv run pytest tests/test_system_auth_models.py::TestSystemUser::test_password_hashing_uses_bcrypt -v -s
```

### Test Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `security`: Security tests
- `auth`: Authentication tests
- `asyncio`: Async tests
- `slow`: Slow-running tests