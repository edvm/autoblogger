# GitHub Workflows Documentation

This directory contains GitHub Actions workflows for the AutoBlogger project. These workflows provide comprehensive CI/CD, security scanning, and automated dependency management.

## 📋 Workflow Overview

### 🔧 Main CI/CD Pipeline (`ci.yml`)

**Triggers:** Push to main/develop, Pull Requests, Manual dispatch

**Purpose:** Main continuous integration pipeline that runs tests, quality checks, and builds.

**Jobs:**
- **Backend Tests** - Python 3.11 & 3.13 matrix testing with both OpenAI and Gemini providers
- **Frontend Tests** - Node.js 18 & 20 matrix testing with TypeScript checks
- **Security Scan** - Bandit, Safety, npm audit, and dependency analysis
- **CodeQL Analysis** - GitHub's semantic code analysis for security vulnerabilities
- **Docker Build** - Multi-architecture container builds and testing
- **Integration Tests** - End-to-end testing with real services
- **CI Success** - Summary job that reports overall pipeline status

**Features:**
- ✅ Matrix testing across Python and Node.js versions
- ✅ LLM provider testing (OpenAI and Gemini)
- ✅ Comprehensive code coverage reporting
- ✅ Intelligent dependency caching
- ✅ Multi-architecture Docker builds
- ✅ Artifact upload for test results and coverage

### 🔒 Security Scanning (`security.yml`)

**Triggers:** Daily at 2 AM UTC, Push to main, Pull Requests, Manual dispatch

**Purpose:** Comprehensive security analysis and vulnerability detection.

**Jobs:**
- **Dependency Review** - Reviews new dependencies in PRs for security issues
- **Python Security** - Bandit static analysis, Safety dependency checks, Semgrep analysis
- **Node.js Security** - npm audit, Snyk vulnerability scanning
- **Container Security** - Trivy vulnerability scanning for Docker images
- **Secret Scanning** - GitLeaks analysis for accidentally committed secrets
- **Security Summary** - Consolidated security report

**Features:**
- ✅ Automated daily security scans
- ✅ Multiple security tools for comprehensive coverage
- ✅ SARIF integration with GitHub Security tab
- ✅ Configurable severity thresholds
- ✅ Security report artifacts

### 🚀 Release & Deploy (`release.yml`)

**Triggers:** Tags (v*), Push to main, Manual dispatch

**Purpose:** Automated releases, Docker image publishing, and deployments.

**Jobs:**
- **Create Release** - Automatic changelog generation and GitHub release creation
- **Build & Publish** - Multi-architecture Docker image builds and registry publishing
- **Deploy** - Environment-specific deployments (staging/production)
- **Notify** - Deployment status notifications and summaries

**Features:**
- ✅ Automatic semantic versioning
- ✅ Changelog generation from git commits
- ✅ Multi-architecture Docker builds (AMD64, ARM64)
- ✅ GitHub Container Registry publishing
- ✅ Environment-specific deployment strategies
- ✅ Deployment status notifications

### 🤖 Dependency Management (`dependabot.yml`)

**Purpose:** Automated dependency updates across all package ecosystems.

**Configurations:**
- **Python Backend** - Weekly updates for pip packages with grouping
- **Node.js Frontend** - Weekly updates for npm packages with grouping
- **GitHub Actions** - Weekly updates for action versions
- **Docker** - Weekly updates for base images

**Features:**
- ✅ Intelligent package grouping (testing, security, UI, etc.)
- ✅ Configurable update schedules
- ✅ Automatic labeling and assignment
- ✅ Version update type filtering
- ✅ Security-focused dependency management

## 🔧 Configuration Files

### `dependency-review-config.yml`
Configuration for dependency review action with:
- License allowlist (MIT, Apache-2.0, BSD, etc.)
- Vulnerability severity thresholds
- Package deny/allow lists
- Custom security policies

### Backend `pyproject.toml` Enhancements
Added comprehensive tool configurations:
- **pytest** - Test discovery, coverage, and reporting
- **coverage** - Branch coverage and exclusion rules  
- **ruff** - Linting and formatting rules
- **mypy** - Type checking configuration

## 🚀 Getting Started

### 1. Required Secrets

Add these secrets to your GitHub repository settings:

```bash
# Optional - for enhanced security scanning
CODECOV_TOKEN=your_codecov_token
SEMGREP_APP_TOKEN=your_semgrep_token  
SNYK_TOKEN=your_snyk_token
GITLEAKS_LICENSE=your_gitleaks_license

# Optional - for testing with real APIs
TAVILY_API_KEY_TEST=your_test_tavily_key
CLERK_SECRET_KEY_TEST=your_test_clerk_key
CLERK_PUBLISHABLE_KEY_TEST=your_test_clerk_key
```

### 2. Environment Setup

Ensure your repository has:
- Protected main branch
- Required status checks enabled
- Branch protection rules configured

### 3. Workflow Permissions

The workflows require these permissions:
- `contents: read/write` (for releases)
- `packages: write` (for Docker registry)
- `security-events: write` (for security scanning)
- `actions: read` (for workflow access)

## 📊 Quality Gates

All workflows enforce these quality standards:

### ✅ Code Quality
- All tests must pass (unit, integration, security)
- Code coverage > 80%
- No linting or formatting violations
- TypeScript type checking passes
- No high/critical security vulnerabilities

### ✅ Security Standards
- Dependency vulnerability scanning
- Static code analysis (Bandit, Semgrep)
- Container image scanning (Trivy)
- Secret detection (GitLeaks)
- License compliance checking

### ✅ Build Standards
- Multi-architecture Docker builds
- Successful builds across all supported environments
- Integration test validation
- Performance benchmark compliance

## 🎯 Workflow Triggers

### Automatic Triggers
- **Push to main/develop** → Full CI pipeline + security scan
- **Pull Request** → CI pipeline + dependency review
- **Tag creation (v*)** → Release pipeline + deployment
- **Daily 2 AM UTC** → Security scanning
- **Weekly Tuesday** → Dependency updates

### Manual Triggers
- All workflows support `workflow_dispatch` for manual execution
- Release workflow supports custom version and environment inputs
- Security workflow can be triggered for immediate vulnerability assessment

## 🔍 Monitoring & Debugging

### Workflow Status
- Check the Actions tab for workflow execution status
- Review job summaries for quick status overview
- Download artifacts for detailed analysis

### Security Reports
- Security findings are uploaded to GitHub Security tab
- Detailed reports available as workflow artifacts
- Daily security scan summaries in workflow logs

### Coverage Reports
- Codecov integration provides coverage tracking
- HTML coverage reports available as artifacts
- Coverage trends visible in PR comments

## 🚀 Performance Optimizations

### Caching Strategy
- **UV dependencies** - Cached with lockfile fingerprint
- **npm dependencies** - Cached with package-lock.json
- **Docker layers** - GitHub Actions cache for faster builds
- **Python packages** - Cached for consistent environments

### Parallel Execution
- Matrix testing runs jobs in parallel
- Independent job execution for faster feedback
- Conditional job execution based on changes

### Resource Optimization
- Targeted job execution based on file changes
- Efficient artifact handling and retention
- Optimized Docker layer caching

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AutoBlogger Setup Guide](../backend/docs/HOWTO_SETUP.md)
- [Security Best Practices](https://docs.github.com/en/code-security)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)

## 🤝 Contributing

When modifying workflows:
1. Test changes in a fork first
2. Use `workflow_dispatch` for testing
3. Update this documentation
4. Follow the existing patterns and naming conventions
5. Ensure backward compatibility