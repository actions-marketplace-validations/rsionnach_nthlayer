# Changelog

## Phase 4: PagerDuty Integration (December 2025)

### Complete PagerDuty Integration
- **Tier-based escalation policies** - Critical (5/15/30min), High (15/30/60min), Medium (30/60min), Low (60min)
- **Auto-creates resources** - Teams, Schedules (primary/secondary/manager), Escalation Policies, Services
- **Team membership** - API key owner automatically added as team manager
- **Support models** - self, shared, sre, business_hours with routing labels
- **Event Orchestration** - Alert routing for shared/sre support models
- **Alertmanager config** - Auto-generated with PagerDuty receiver, tier-based timing
- **Official SDK** - Uses `pagerduty.RestApiV2Client` (not bespoke HTTP client)
- **Resilient setup** - Continues creating resources even if some fail
- 38+ tests for PagerDuty and Alertmanager modules

### CLI Improvements
- Clean one-line per resource type output
- Verbose mode (`--verbose`) for file list and details
- Warnings grouped at end
- Removed cluttery box drawing

## Phase 3: Observability Suite (December 2025)

### Phase 3D: Polish & Documentation
- Added dashboard customization (--full flag for 28+ panels)
- Created comprehensive observability guide (500 lines)
- Updated README and presentations
- 84/84 tests passing

### Phase 3C: Recording Rules
- Implemented Prometheus recording rules generation
- 20+ pre-computed metrics per service
- CLI command: `generate-recording-rules`
- 10x dashboard performance improvement

### Phase 3B: Technology Templates
- Created 4 technology templates (40 panels total)
- PostgreSQL (12 panels), Redis (10), Kubernetes (10), HTTP/API (8)
- Template registry system
- Dashboards improved from 6 → 12 → 28 panels

### Phase 3A: Dashboard Foundation
- Implemented Grafana dashboard generation
- Dashboard models and builder
- CLI command: `generate-dashboard`
- 6-12 panels per service with SLO, health, and technology metrics

## Weeks 7-8: Multi-Environment Support

- Multi-environment configuration system (dev, staging, prod)
- Environment-specific overrides
- Auto-detection from 12+ CI/CD sources
- Variable substitution (${env}, ${service}, ${team})
- CLI commands: `list-environments`, `diff-envs`, `validate-env`

## Weeks 1-6: Foundation

### Alert Generation
- 400+ battle-tested alert rules from awesome-prometheus-alerts
- Auto-generated alerts for PostgreSQL, Redis, MySQL, MongoDB, Kafka, etc.
- CLI command: `generate-alerts`

### Core Features
- SLO generation from service specifications
- PagerDuty integration with auto-service creation
- Prometheus integration for error budget tracking
- Deployment correlation and gates
- Custom template system
- CLI with 10 commands

## Stats

- **Commands:** 10 total
- **Tests:** 84/84 passing (100%)
- **Documentation:** 25,000+ words
- **Dashboard Panels:** 40 in template library
- **Alert Rules:** 400+
