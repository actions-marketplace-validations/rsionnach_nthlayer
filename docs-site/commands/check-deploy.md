# check-deploy

Check if deployment should be allowed based on error budget.

## Synopsis

```bash
nthlayer check-deploy <service-file> [options]
```

## Description

The `check-deploy` command queries Prometheus for SLO metrics, calculates error budget consumption, and determines if deployment should proceed.

This enables **Shift Left** reliability - catching issues before they reach production by blocking deploys when error budget is exhausted.

## Exit Codes

| Code | Result | Meaning |
|------|--------|---------|
| 0 | Approved | Budget healthy, safe to deploy |
| 1 | Warning | Budget low, deploy with caution |
| 2 | Blocked | Budget exhausted, do not deploy |

## Options

| Option | Description |
|--------|-------------|
| `--prometheus-url URL` | Prometheus server URL (or use `PROMETHEUS_URL` env var) |
| `--environment ENV` | Environment name (dev, staging, prod) |
| `--demo` | Show demo output with sample data |

## Examples

### Basic Check

```bash
nthlayer check-deploy services/payment-api.yaml \
  --prometheus-url http://prometheus:9090
```

### With Environment

```bash
nthlayer check-deploy services/api.yaml \
  --prometheus-url http://prometheus:9090 \
  --environment prod
```

### CI/CD Integration

```bash
# In GitHub Actions, GitLab CI, etc.
nthlayer check-deploy services/api.yaml \
  --prometheus-url "$PROMETHEUS_URL"

if [ $? -eq 2 ]; then
  echo "Deployment blocked - error budget exhausted"
  exit 1
fi
```

## Custom Thresholds

Override default tier-based thresholds with a `DeploymentGate` resource:

```yaml
# service.yaml
resources:
  - kind: DeploymentGate
    name: custom-gate
    spec:
      thresholds:
        warning: 30    # Warn when <30% budget remaining
        blocking: 5    # Block when <5% budget remaining
```

## Conditional Policies

Add time-based or context-aware conditions:

```yaml
resources:
  - kind: DeploymentGate
    name: smart-gate
    spec:
      thresholds:
        warning: 20
        blocking: 10

      conditions:
        # Stricter during business hours
        - name: business-hours
          when: "hour >= 9 AND hour <= 17 AND weekday"
          blocking: 15

        # Complete freeze during holidays
        - name: holiday-freeze
          when: "freeze_period('2024-12-20', '2025-01-02')"
          blocking: 100

      exceptions:
        # SRE can bypass gate
        - team: sre-oncall
          allow: always
```

## Condition Language

The condition evaluator supports:

### Comparisons
```
hour >= 9
budget_remaining < 20
tier == 'critical'
```

### Boolean Operators
```
hour >= 9 AND hour <= 17
weekday OR environment == 'dev'
NOT freeze_period
```

### Built-in Functions
```
business_hours()                           # Mon-Fri 9-17
weekday()                                  # Mon-Fri
freeze_period('2024-12-20', '2025-01-02') # Date range
```

### Available Variables

| Variable | Description |
|----------|-------------|
| `hour` | Current hour (0-23) |
| `weekday` | True if Mon-Fri |
| `date` | Current date (YYYY-MM-DD) |
| `budget_remaining` | Budget remaining % |
| `budget_consumed` | Budget consumed % |
| `tier` | Service tier |
| `environment` | Deployment environment |
| `downstream_count` | Number of downstream services |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PROMETHEUS_URL` | Prometheus server URL |
| `PROMETHEUS_USERNAME` | Basic auth username |
| `PROMETHEUS_PASSWORD` | Basic auth password |

## CI/CD Integrations

See the [CI/CD integration examples](https://github.com/nthlayer/nthlayer/tree/main/examples/cicd) for:

- GitHub Actions
- ArgoCD (PreSync hook)
- GitLab CI
- Tekton

## See Also

- [Deployment Gates Concept](../concepts/deployment-gates.md)
- [SLO Command](./slo.md)
- [Portfolio Command](./portfolio.md)
