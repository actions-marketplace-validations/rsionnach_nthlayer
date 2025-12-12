# NthLayer ArgoCD Integration

Block ArgoCD syncs when error budget is exhausted using PreSync hooks.

## How It Works

1. ArgoCD detects a sync is needed
2. PreSync hook runs `nthlayer check-deploy`
3. If budget is healthy (exit 0) or warning (exit 1): sync proceeds
4. If budget is exhausted (exit 2): sync is blocked

## Setup

### 1. Create Prometheus Secret

```bash
kubectl create secret generic prometheus-credentials \
  --from-literal=url=https://prometheus.example.com \
  --from-literal=username=admin \
  --from-literal=password=secret
```

### 2. Add Hook to Your Application

Copy `deployment-gate-hook.yaml` to your application's manifest directory and customize:

- Update the `service.yaml` ConfigMap with your service config
- Adjust environment variables as needed

### 3. Deploy

ArgoCD will automatically run the gate check before each sync.

## Files

| File | Description |
|------|-------------|
| `deployment-gate-hook.yaml` | Complete example with ConfigMap and Job |

## Customization

### Custom Thresholds

Add a `DeploymentGate` resource to your service.yaml:

```yaml
resources:
  - kind: DeploymentGate
    name: my-gate
    spec:
      thresholds:
        warning: 30    # Warn when <30% remaining
        blocking: 5    # Block when <5% remaining
```

### Conditional Blocking

Add conditions for time-based or context-aware gates:

```yaml
resources:
  - kind: DeploymentGate
    name: smart-gate
    spec:
      thresholds:
        warning: 20
        blocking: 10
      conditions:
        - name: business-hours
          when: "hour >= 9 AND hour <= 17 AND weekday"
          blocking: 15  # Stricter during business hours
        - name: holiday-freeze
          when: "freeze_period('2024-12-20', '2025-01-02')"
          blocking: 100  # Complete freeze
```

## Troubleshooting

### Hook Fails to Run

Check that the secret exists:
```bash
kubectl get secret prometheus-credentials
```

### Gate Always Blocks

Check Prometheus connectivity:
```bash
kubectl run --rm -it test --image=curlimages/curl -- \
  curl -s "http://prometheus:9090/api/v1/query?query=up"
```

### View Hook Logs

```bash
kubectl logs job/nthlayer-deployment-gate
```
