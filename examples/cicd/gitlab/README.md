# NthLayer GitLab CI Integration

Block deployments when error budget is exhausted using GitLab CI templates.

## Quick Start

### 1. Copy the Template

Copy `.nthlayer-gate.yml` to your repository root.

### 2. Configure CI/CD Variables

In GitLab Settings > CI/CD > Variables:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `PROMETHEUS_URL` | `https://prometheus.example.com` | Yes | No |
| `PROMETHEUS_USERNAME` | (optional) | Yes | No |
| `PROMETHEUS_PASSWORD` | (optional) | Yes | Yes |

### 3. Update Your Pipeline

```yaml
# .gitlab-ci.yml
include:
  - local: '.nthlayer-gate.yml'

stages:
  - gate
  - deploy

# Gate check runs first
check-gate:
  extends: .nthlayer-gate
  stage: gate
  variables:
    SERVICE_FILE: services/my-service.yaml

# Deploy only if gate passes
deploy:
  stage: deploy
  needs: [check-gate]
  script:
    - kubectl apply -f k8s/
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## Advanced Usage

### Combined Gate + Deploy Job

```yaml
deploy:
  extends: .deploy-with-gate
  variables:
    SERVICE_FILE: services/api.yaml
  script:
    - nthlayer check-deploy "$SERVICE_FILE" --prometheus-url "$PROMETHEUS_URL"
    - ./deploy.sh
```

### Allow Warning Deployments

```yaml
check-gate:
  extends: .nthlayer-gate
  allow_failure:
    exit_codes:
      - 1  # Allow warnings through
```

### Environment-Specific Gates

```yaml
.gate-prod:
  extends: .nthlayer-gate
  variables:
    ENVIRONMENT: prod

.gate-staging:
  extends: .nthlayer-gate
  variables:
    ENVIRONMENT: staging
  allow_failure: true  # Staging is advisory only
```

## Exit Codes

| Code | Result | Pipeline Effect |
|------|--------|-----------------|
| 0 | Approved | Job passes |
| 1 | Warning | Job passes (with warning) |
| 2 | Blocked | Job fails, pipeline stops |
