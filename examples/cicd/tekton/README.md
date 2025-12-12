# NthLayer Tekton Integration

Block Tekton pipelines when error budget is exhausted.

## Quick Start

### 1. Install the Task

```bash
kubectl apply -f nthlayer-gate-task.yaml
```

### 2. Create Prometheus Secret (Optional)

```bash
kubectl create secret generic prometheus-credentials \
  --from-literal=username=admin \
  --from-literal=password=secret
```

### 3. Use in Your Pipeline

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: my-deploy-pipeline
spec:
  tasks:
    - name: check-gate
      taskRef:
        name: nthlayer-deployment-gate
      params:
        - name: service-file
          value: services/my-service.yaml
        - name: prometheus-url
          value: https://prometheus.example.com

    - name: deploy
      runAfter: [check-gate]
      taskRef:
        name: deploy-app
```

## Task Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `service-file` | Yes | - | Path to service.yaml |
| `prometheus-url` | Yes | - | Prometheus server URL |
| `environment` | No | `prod` | Environment (dev, staging, prod) |
| `nthlayer-version` | No | `latest` | NthLayer version to install |

## Task Results

| Result | Description |
|--------|-------------|
| `result` | Gate result: `approved`, `warning`, or `blocked` |
| `budget-remaining` | Error budget remaining percentage |

## Conditional Deployment

Use `when` expressions to control downstream tasks:

```yaml
- name: deploy
  runAfter: [check-gate]
  taskRef:
    name: deploy-app
  when:
    - input: $(tasks.check-gate.results.result)
      operator: in
      values: ["approved", "warning"]
```

## Files

| File | Description |
|------|-------------|
| `nthlayer-gate-task.yaml` | Task definition + example Pipeline |
