# NthLayer CI/CD Integrations

Block deployments when error budget is exhausted using native CI/CD integrations.

## Available Integrations

| Platform | Directory | Description |
|----------|-----------|-------------|
| **GitHub Actions** | `github-action/` | Reusable GitHub Action |
| **ArgoCD** | `argocd/` | PreSync hook for GitOps |
| **GitLab CI** | `gitlab/` | Reusable CI template |
| **Tekton** | `tekton/` | Reusable Tekton Task |

## How It Works

All integrations use the `nthlayer check-deploy` command which:

1. Parses your `service.yaml` for SLO definitions
2. Queries Prometheus for current SLI values
3. Calculates error budget consumption
4. Returns exit code based on budget health

### Exit Codes

| Code | Result | Meaning |
|------|--------|---------|
| 0 | Approved | Budget healthy, safe to deploy |
| 1 | Warning | Budget low, deploy with caution |
| 2 | Blocked | Budget exhausted, do not deploy |

## Quick Start

### 1. Define Your SLOs

Create a `service.yaml` with SLO definitions:

```yaml
service:
  name: my-api
  team: platform
  tier: critical
  type: api

resources:
  - kind: SLO
    name: availability
    spec:
      objective: 99.95
      window: 30d
      indicator:
        query: |
          sum(rate(http_requests_total{service="${service}",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="${service}"}[5m]))
```

### 2. Choose Your Integration

See the platform-specific README in each directory:

- [GitHub Actions](github-action/README.md)
- [ArgoCD](argocd/README.md)
- [GitLab CI](gitlab/README.md)
- [Tekton](tekton/README.md)

## Custom Policies

Override default thresholds with a `DeploymentGate` resource:

```yaml
resources:
  - kind: DeploymentGate
    name: custom-gate
    spec:
      thresholds:
        warning: 30    # Warn when <30% remaining
        blocking: 5    # Block when <5% remaining

      conditions:
        - name: business-hours
          when: "hour >= 9 AND hour <= 17 AND weekday"
          blocking: 15  # Stricter during business hours

      exceptions:
        - team: sre-oncall
          allow: always  # SRE can bypass
```

## Environment Variables

All integrations support these environment variables:

| Variable | Description |
|----------|-------------|
| `PROMETHEUS_URL` | Prometheus server URL |
| `PROMETHEUS_USERNAME` | Basic auth username (optional) |
| `PROMETHEUS_PASSWORD` | Basic auth password (optional) |

## Testing Locally

Test the gate check locally before integrating:

```bash
# Install NthLayer
pip install nthlayer

# Run gate check
nthlayer check-deploy services/my-service.yaml \
  --prometheus-url http://localhost:9090 \
  --environment prod

# Check exit code
echo "Exit code: $?"
```
