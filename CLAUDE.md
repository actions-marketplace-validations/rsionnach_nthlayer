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
- `/project:spec-to-beads <spec-file>` — Decompose a spec into Beads issues with dependency tracking. Do NOT implement — only create the task graph.

### Autonomous Execution
- Ralph loop prompt: `.claude/ralph-prompt.md`
- Ralph loop runner: `.claude/ralph-loop.sh [max-iterations]`
- Completion promise: `RALPH_COMPLETE`

### Specs
Specification files live in `specs/` (or wherever the project currently stores them). When implementing from a spec, always reference the spec file path in Beads task notes for traceability. If you make architectural decisions that diverge from the spec, document them in the task's notes field.

<!-- AUTO-MANAGED: learned-patterns -->
<!-- /AUTO-MANAGED: learned-patterns -->

<!-- AUTO-MANAGED: discovered-conventions -->
<!-- /AUTO-MANAGED: discovered-conventions -->
