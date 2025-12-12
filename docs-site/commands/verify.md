# nthlayer verify

Verify that declared metrics exist in Prometheus before promoting to production.

This implements the **Contract Verification** pattern - ensuring that metrics declared in `service.yaml` actually exist before deployment promotion.

## Usage

```bash
nthlayer verify <service.yaml> [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--prometheus-url, -p URL` | Target Prometheus URL |
| `--env ENVIRONMENT` | Environment name (dev, staging, prod) |
| `--no-fail` | Don't fail on missing metrics (always exit 0) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PROMETHEUS_URL` | Default Prometheus URL (if `--prometheus-url` not provided) |
| `PROMETHEUS_USERNAME` | Basic auth username |
| `PROMETHEUS_PASSWORD` | Basic auth password |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All metrics verified |
| `1` | Optional metrics missing (warning) |
| `2` | Critical SLO metrics missing (block promotion) |

## Examples

### Basic Verification

```bash
nthlayer verify checkout-service.yaml --prometheus-url http://prometheus:9090
```

Output:
```
╭──────────────────────────────────────────────────────────────────────────────╮
│ Contract Verification: checkout-service                                       │
╰──────────────────────────────────────────────────────────────────────────────╯

Target: http://prometheus:9090
Service: checkout-service

SLO Metrics (Critical):
  ✓ http_requests_total
  ✓ http_request_duration_seconds_bucket

Observability Metrics (Optional):
  ✓ checkout_started_total
  ✓ checkout_completed_total

Summary:
  Total: 4 metrics
  ✓ Verified: 4

✓ All declared metrics verified
Contract verification passed - safe to promote
```

### CI/CD Pipeline Integration

```bash
# Verify against sandbox before promoting to production
nthlayer verify service.yaml -p $SANDBOX_PROMETHEUS_URL

# Exit code determines pipeline gate
if [ $? -eq 2 ]; then
  echo "Critical metrics missing - blocking promotion"
  exit 1
fi
```

### Missing Metrics Output

When critical metrics are missing:

```
SLO Metrics (Critical):
  ✓ http_requests_total
  ✗ payment_processed_total ← MISSING

Summary:
  Total: 4 metrics
  ✓ Verified: 3
  ✗ Critical missing: 1

✗ Critical SLO metrics missing - blocking promotion

Recommendations:
  • Ensure payment_processed_total is instrumented
  • Run integration tests to generate traffic before re-verifying
```

## What Gets Verified

### SLO Indicator Metrics (Critical)

Metrics extracted from SLO indicator queries in `service.yaml`:

```yaml
resources:
  - kind: SLO
    name: availability
    spec:
      indicators:
        - type: availability
          success_ratio:
            total_query: sum(rate(http_requests_total{service="checkout"}[5m]))
            good_query: sum(rate(http_requests_total{service="checkout",status!~"5.."}[5m]))
```

Extracts: `http_requests_total` → **Critical** (blocks promotion if missing)

### Observability Metrics (Optional)

Metrics declared in the Observability resource:

```yaml
resources:
  - kind: Observability
    name: observability
    spec:
      metrics:
        - checkout_started_total
        - checkout_completed_total
```

These are **Optional** (warning only if missing, doesn't block promotion)

## Philosophy

**"Declarative First, Verify Later"**

| Step | Runtime Required? | Description |
|------|-------------------|-------------|
| `nthlayer apply` | No | Generate configs from declarations (Shift Left) |
| `nthlayer verify` | Yes | Verify contract before promotion |

This solves the "Chicken and Egg" problem:
- You can generate production-ready configs without the service running
- You verify the contract in lower environments before promoting

## Tekton Pipeline Example

```yaml
tasks:
  - name: generate-configs
    taskRef:
      name: nthlayer-apply
    params:
      - name: service-file
        value: services/checkout-service.yaml

  - name: deploy-to-sandbox
    runAfter: [generate-configs]
    taskRef:
      name: deploy

  - name: verify-metrics
    runAfter: [deploy-to-sandbox]
    taskRef:
      name: nthlayer-verify
    params:
      - name: service-file
        value: services/checkout-service.yaml
      - name: prometheus-url
        value: $(params.sandbox-prometheus-url)

  - name: deploy-to-production
    runAfter: [verify-metrics]  # Blocked if verify fails
    taskRef:
      name: deploy
```

## GitHub Actions Example

```yaml
jobs:
  verify-and-promote:
    steps:
      - name: Deploy to Staging
        run: kubectl apply -f generated/

      - name: Wait for Metrics
        run: sleep 60  # Allow time for metrics to appear

      - name: Verify Contract
        run: |
          nthlayer verify service.yaml \
            --prometheus-url ${{ secrets.STAGING_PROMETHEUS_URL }}

      - name: Promote to Production
        if: success()
        run: kubectl apply -f generated/ --context production
```

## See Also

- [Service YAML Schema](../reference/service-yaml.md) - Full spec reference
- [nthlayer apply](./apply.md) - Generate configs
- [CLI Reference](../reference/cli.md) - All commands
