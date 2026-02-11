# CLAUDE.md
This repo's agent instructions live in AGENTS.md.

## Mission
NthLayer: Reliability at build time, not incident time. Validate production readiness in CI/CD (Generate → Validate → Gate).

## How to work in this repo
- Keep changes small and testable (PR-sized chunks).
- Prefer refactors that reduce touch points for adding templates/backends.
- Keep CLI thin; move business logic into modules/classes.
- Always update/extend tests when changing behavior.
- Never commit secrets (use env vars).

<!-- AUTO-MANAGED: architecture -->
## Architecture

### Core Modules
- `orchestrator.py` - Service orchestration: coordinates SLO, alert, dashboard generation from service YAML
- `dashboards/` - Intent-based dashboard generation with metric resolution
  - `resolver.py` - MetricResolver: translates intents to Prometheus metrics with fallback chains
  - `templates/` - Technology-specific intent templates (postgresql, redis, kafka, etc.)
  - `builder_sdk.py` - Grafana dashboard construction using grafana-foundation-sdk
- `discovery/` - Metric discovery from Prometheus
  - `client.py` - MetricDiscoveryClient: queries Prometheus for available metrics
  - `classifier.py` - Classifies metrics by technology and type
- `dependencies/` - Dependency discovery and graphing
  - `discovery.py` - DependencyDiscovery orchestrator
  - `providers/` - kubernetes, prometheus, consul, etcd, backstage providers
- `deployments/` - Deployment detection via webhooks
  - `base.py` - BaseDeploymentProvider ABC and DeploymentEvent model
  - `registry.py` - Provider registry for webhook routing
  - `providers/` - argocd, github, gitlab webhook parsers
  - `errors.py` - DeploymentProviderError exception
- `providers/` - External service integrations (grafana, prometheus, pagerduty, mimir)
- `identity/` - Service identity resolution across naming conventions
- `slos/` - SLO definition, validation, and recording rule generation
  - `deployment.py` - DeploymentRecorder for storing deployment events
- `alerts/` - Alert rule generation from dependencies and SLOs
- `validation/` - Metadata and resource validation
- `api/` - FastAPI webhook endpoints
  - `routes/webhooks.py` - Deployment webhook receiver

### Data Flow
1. Service YAML → ServiceOrchestrator → ResourceDetector (indexes by kind)
2. ResourceDetector determines what to generate (SLOs, alerts, dashboards, etc.)
3. Dashboard generation: IntentTemplate.get_panel_specs() → MetricResolver.resolve() → Panel objects
4. Metric resolution: Custom overrides → Discovery → Fallback chain → Guidance
5. Resource creation: Async providers apply changes (Grafana, PagerDuty, etc.)
6. Deployment webhooks: Provider parses webhook → DeploymentEvent → DeploymentRecorder → Database
<!-- /AUTO-MANAGED: architecture -->

## Task Tracking with Beads (bd)

This project uses [beads](https://github.com/steveyegge/beads) for issue tracking. **Always use the `bd` CLI** - never create individual JSON files in `.beads/`.

### Essential Commands
```bash
bd ready              # Show tasks ready to work on (no blockers)
bd list               # List all issues
bd list --status open # List open issues only
bd show <id>          # Show issue details
bd create --title "..." --description "..." --priority 1 --type feature
bd update <id> --status in_progress
bd close <id> --reason "What was done"
bd comment <id> "Comment text"
bd stats              # Project statistics
bd blocked            # Show blocked issues
bd dep tree <id>      # Show dependency tree
```

### Workflow
1. Check what's ready: `bd ready`
2. Start work: `bd update <id> --status in_progress`
3. Do the work
4. Close when done: `bd close <id> --reason "Description"`
5. Check next task: `bd ready`

### Linking to Specifications
For detailed feature specs, add a comment to the bd issue:
```bash
bd comment <id> "Specification: FEATURE_SPEC.md - Full implementation details."
```

### File Structure (DO NOT MODIFY MANUALLY)
```
.beads/
├── issues.jsonl    # Source of truth (managed by bd)
├── config.yaml     # Configuration
├── metadata.json   # Metadata
└── beads.db       # SQLite cache (gitignored)
```

## Commands
- Tests: `make test`
- Lint: `make lint` / `make lint-fix`
- Typecheck: `make typecheck`
- Format: `make format`
- Lock deps: `make lock` / `make lock-upgrade`

## Releases
- PyPI uses trusted publisher (no token needed)
- Create a GitHub release → triggers `.github/workflows/release.yml` → auto-publishes to PyPI
- Version is defined **only** in `pyproject.toml` (single source of truth via importlib.metadata)
- **CHANGELOG.md must be updated** before every release with all changes since the last release

## Workflow Tooling

### Beads
This project uses [Beads](https://github.com/steveyegge/beads) for task tracking. Always use `bd` commands for work management. See `AGENTS.md` for the full Beads workflow.

### Session Lifecycle
- **SessionStart hook** automatically loads Beads state and recent spec changes
- **Stop hook** enforces "land the plane" discipline — you cannot end a session with uncommitted changes, unpushed commits, or stale in-progress beads

### Slash Commands
- `/spec-to-beads <spec-file>` — Decompose a spec into Beads issues with dependency tracking. Do NOT implement — only create the task graph.

### Autonomous Execution
- Ralph loop prompt: `.claude/ralph-prompt.md`
- Ralph loop runner: `.claude/ralph-loop.sh [max-iterations]`
- Completion promise: `RALPH_COMPLETE`

### Specs
Specification files live in `specs/` (or wherever the project currently stores them). When implementing from a spec, always reference the spec file path in Beads task notes for traceability. If you make architectural decisions that diverge from the spec, document them in the task's notes field.

## Code Review & Audit Rules

### Architectural invariants
- Dashboard generation must use `IntentBasedTemplate` subclasses and `grafana-foundation-sdk` — no raw JSON dashboard construction
- Metric resolution must go through the resolver (`dashboards/resolver.py`) — do not hardcode metric names in templates
- All PromQL must use `service="$service"` label selector (not `cluster` or other labels)
- `histogram_quantile` must include `sum by (le)` — bare `rate()` inside `histogram_quantile` is always a bug
- Rate queries must aggregate: `sum(rate(metric{service="$service"}[5m]))`
- Status label conventions must match service type: API (`status!~"5.."`), Worker (`status!="failed"`), Stream (`status!="error"`)
- Error handling must use `NthLayerError` subclasses — bare `Exception` or `RuntimeError` raises are not allowed
- CLI commands must be thin — business logic lives in modules/classes, not in click command functions
- CLI output must go through `ux.py` helpers — no raw `print()` or `click.echo()` in command handlers
- External service integrations must use official SDKs (`grafana-foundation-sdk`, `pagerduty`, `boto3`) — no bespoke HTTP clients
- Exit codes must follow convention: 0=success, 1=warning/error, 2=critical/blocked

### Known intentional patterns (do not flag)
- Demo app intentionally missing metrics (`redis_db_keys` from notification-worker, `elasticsearch_jvm_memory_*` from search-api) to demonstrate guidance panels
- Legacy template patterns that are tracked as known tech debt in Beads
- Empty catch blocks in migration code are intentional (best-effort migration)
- Lenient validation in `nthlayer validate-metadata` is by design (warns, doesn't fail)

### Slash Commands
- `/audit-codebase` — Run a systematic codebase audit using the code-auditor subagent. Files findings as dual Beads + GitHub Issues.

<!-- AUTO-MANAGED: learned-patterns -->
## Learned Patterns

### Intent-Based Dashboard Generation
- Templates extend `IntentBasedTemplate` (from `dashboards/templates/base_intent.py`)
- Define panels using abstract "intents" instead of hardcoded metric names
- `get_panel_specs()` returns `List[PanelSpec]` with intent references
- `MetricResolver` translates intents to actual Prometheus metrics at generation time
- Resolution waterfall: custom overrides → primary discovery → fallback chain → guidance panels
- Example: `postgresql.connections` intent resolves to `pg_stat_database_numbackends` or fallback

### Metric Discovery and Resolution
- `MetricDiscoveryClient` (discovery/client.py) queries Prometheus for available metrics
- `MetricResolver` (dashboards/resolver.py) resolves intents with fallback chains
- `discover_for_service(service_name)` populates discovered metrics cache
- `resolve(intent_name)` returns `ResolutionResult` with status (resolved/fallback/unresolved)
- Unresolved intents generate guidance panels with exporter installation instructions
- Supports custom metric overrides from service YAML

### Async Provider Pattern
- All providers implement async interface: `async def health_check()`, `async def apply()`
- Use `asyncio.to_thread()` for sync HTTP clients (httpx.Client) to avoid blocking
- Dependency providers implement `async def discover(service)` and `async def discover_downstream(service)`
- DependencyDiscovery orchestrator runs providers in parallel with `asyncio.gather()`
- Provider errors raise `ProviderError` subclasses, never bare `Exception` or `RuntimeError`

### Service Orchestration
- `ServiceOrchestrator` (orchestrator.py) coordinates resource generation from service YAML
- `ResourceDetector` builds single-pass index of resources by kind (SLO, Dependencies, etc.)
- Auto-generates recording rules and Backstage entities when SLOs exist
- Auto-generates alerts and dashboards when dependencies exist
- `plan()` returns preview, `apply()` executes generation

### Deployment Detection Provider Pattern
- Provider-agnostic webhook handling via `BaseDeploymentProvider` ABC
- Each provider implements `verify_webhook()` (signature validation) and `parse_webhook()` (payload parsing)
- Providers return `DeploymentEvent` intermediate model (service, commit_sha, environment, author, etc.)
- `DeploymentProviderRegistry` maps provider names to implementations
- Webhook route dispatches based on `/webhooks/deployments/{provider_name}` path parameter
- `DeploymentRecorder.record_event()` stores events to database for correlation analysis
- Self-registering providers: import triggers `register_deployment_provider()` at module load
- Supported providers: ArgoCD (app.sync.succeeded), GitHub Actions (workflow_run.completed), GitLab (Pipeline Hook)
<!-- /AUTO-MANAGED: learned-patterns -->

<!-- AUTO-MANAGED: discovered-conventions -->
## Discovered Conventions

### Error Handling
- Always raise `ProviderError` or `NthLayerError` subclasses for application errors
- Never use bare `Exception` or `RuntimeError` in application code
- Provider modules define their own error subclasses: `GrafanaProviderError(ProviderError)`
- Import errors from `nthlayer.core.errors`

### Dashboard Template Architecture
- Templates live in `src/nthlayer/dashboards/templates/`
- Technology-specific templates: `{technology}_intent.py` (e.g., `postgresql_intent.py`, `redis_intent.py`)
- All intent templates extend `IntentBasedTemplate` base class
- Base class implements `get_panels()` which calls template's `get_panel_specs()`
- Never construct raw JSON dashboards - always use `grafana-foundation-sdk` and intent templates

### Dependency Discovery
- Provider implementations in `src/nthlayer/dependencies/providers/`
- Each provider extends `BaseDepProvider` with async `discover()` and `discover_downstream()`
- Providers: kubernetes, prometheus, consul, etcd, zookeeper, backstage
- `DependencyDiscovery` (dependencies/discovery.py) orchestrates multiple providers
- Uses `IdentityResolver` to normalize service names across providers

### Deployment Detection
- Deployment providers in `src/nthlayer/deployments/providers/`
- Each provider extends `BaseDeploymentProvider` with `verify_webhook()` and `parse_webhook()`
- Providers: argocd, github, gitlab
- `DeploymentProviderRegistry` (deployments/registry.py) manages provider registration
- Webhook signature verification via HMAC SHA256 (X-Hub-Signature-256, X-Argo-Signature headers)

### Async/Await Usage
- All provider operations are async (health checks, resource creation, discovery)
- Use `asyncio.to_thread()` for sync HTTP operations to avoid blocking event loop
- Parallel operations use `asyncio.gather()` with `return_exceptions=True`
- Provider interfaces define `async def aclose()` for cleanup
<!-- /AUTO-MANAGED: discovered-conventions -->
