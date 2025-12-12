# NthLayer GitHub Action

Check error budget before deployment using NthLayer deployment gates.

## Usage

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Check deployment gate before deploying
      - name: Check Deployment Gate
        uses: nthlayer/nthlayer/.github/actions/deployment-gate@main
        with:
          service-file: services/my-service.yaml
          prometheus-url: ${{ secrets.PROMETHEUS_URL }}
          environment: prod

      # Only runs if gate passed
      - name: Deploy
        run: kubectl apply -f k8s/
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `service-file` | Yes | - | Path to service.yaml |
| `prometheus-url` | Yes | - | Prometheus server URL |
| `environment` | No | `prod` | Environment (dev, staging, prod) |
| `prometheus-username` | No | - | Basic auth username |
| `prometheus-password` | No | - | Basic auth password |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Gate result: `approved`, `warning`, or `blocked` |
| `budget-remaining` | Error budget remaining percentage |

## Exit Codes

- `0` - Deployment approved
- `1` - Warning (proceeds but logs warning)
- `2` - Blocked (fails the workflow)

## Example with Conditional Deploy

```yaml
- name: Check Deployment Gate
  id: gate
  uses: nthlayer/nthlayer/.github/actions/deployment-gate@main
  with:
    service-file: services/api.yaml
    prometheus-url: ${{ secrets.PROMETHEUS_URL }}

- name: Deploy (if approved)
  if: steps.gate.outputs.result == 'approved'
  run: ./deploy.sh

- name: Deploy with caution (if warning)
  if: steps.gate.outputs.result == 'warning'
  run: |
    echo "::warning::Deploying with low error budget"
    ./deploy.sh --canary
```
