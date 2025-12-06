# Live Demo

<div class="demo-banner" markdown>
**[Launch Interactive Demo :material-open-in-new:](demo/index.html){ .md-button .md-button--primary target="_blank" }**
</div>

Experience NthLayer's complete reliability stack generation with live examples.

## What's in the Demo

### Live Grafana Dashboards

See auto-generated dashboards for 6 production services:

| Service | Technologies | Dashboard |
|---------|--------------|-----------|
| **payment-api** | PostgreSQL + Redis | [View Dashboard](https://nthlayer.grafana.net/d/payment-api-overview) |
| **checkout-service** | MySQL + Redis | [View Dashboard](https://nthlayer.grafana.net/d/checkout-service-overview) |
| **notification-worker** | Redis | [View Dashboard](https://nthlayer.grafana.net/d/notification-worker-overview) |
| **analytics-stream** | MongoDB + Redis | [View Dashboard](https://nthlayer.grafana.net/d/analytics-stream-overview) |
| **identity-service** | PostgreSQL + Redis | [View Dashboard](https://nthlayer.grafana.net/d/identity-service-overview) |
| **search-api** | Elasticsearch + Redis | [View Dashboard](https://nthlayer.grafana.net/d/search-api-overview) |

### Generated Alerts

118 production-ready Prometheus alerts across all services, including:

- PostgreSQL: Connection limits, replication lag, deadlocks
- Redis: Memory usage, connection limits, evictions
- Elasticsearch: Cluster health, JVM heap, disk space
- And more...

### SLO Portfolio

Track org-wide reliability with tier-based health scoring:

```
Organization Health: 78% (14/18 services meeting SLOs)

By Tier:
  Critical:  ████████░░  83% (5/6 services)
  Standard:  ███████░░░  75% (6/8 services)
  Low:       ███████░░░  75% (3/4 services)
```

### PagerDuty Integration

Complete incident response setup with:

- Auto-created teams with manager roles
- Tier-based escalation policies (5/15/30 min)
- Support models: self, shared, SRE, business hours

## Try It Yourself

```bash
# Install
pipx install nthlayer

# Interactive setup
nthlayer setup

# Generate configs
nthlayer apply payment-api.yaml

# View portfolio
nthlayer portfolio
```

## Additional Tools

- [ROI Calculator](demo/roi-calculator.html) - Calculate time savings for your organization
- [Demo Comparison](demo/demo-comparison.html) - Before/after comparison

<style>
.demo-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 2rem;
}
.demo-banner .md-button {
    font-size: 1.2rem;
}
</style>
