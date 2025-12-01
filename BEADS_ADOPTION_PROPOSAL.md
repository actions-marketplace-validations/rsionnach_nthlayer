# Beads Adoption Proposal for NthLayer

**Date:** December 1, 2025  
**Status:** Proposal  
**Decision:** Pending

---

## Problem Statement

NthLayer has grown massively in the past month:
- **55 markdown files** across multiple directories
- **21 _COMPLETE.md files** documenting finished work
- **Roadmap items** spread across 8+ different files
- **Feature tracking** fragmented (SOLO_FOUNDER_ROADMAP.md, IMPROVEMENTS.md, OPERATIONAL_CONFIGS_EXPANSION.md, etc.)
- **No dependency tracking** - can't tell what blocks what
- **No "ready to work" detection** - hard to know what can be done next
- **Manual coordination** between documentation files

This is becoming unmanageable for a solo founder with an AI coding agent.

---

## What is Beads?

**Beads** = "A memory upgrade for your coding agent" by Steve Yegge

### Core Capabilities:

1. **Dependency-Aware Issue Tracking**
   - Track issues with `depends_on` relationships
   - Automatic "ready work" detection (issues with no open blockers)
   - Cycle detection to prevent circular dependencies

2. **Git-Backed Storage**
   - Issues stored in `.beads/issues.jsonl` (JSONL = JSON Lines)
   - Can be committed to git like any file
   - Merge-friendly format (line-per-issue)
   - SQLite database for fast queries (auto-generated from JSONL)

3. **AI-Agent Friendly**
   - Designed specifically for coding agents (Claude Code, Cursor, etc.)
   - Simple CLI: `bd create`, `bd list`, `bd ready`
   - MCP integration available (Agent Mail for multi-agent coordination)
   - No UI required (though 3rd-party UIs exist)

4. **Lightweight & Fast**
   - 130k lines of Go code, stable (v0.27.0)
   - Daemon mode for instant queries (<50ms)
   - No external dependencies (just git + SQLite)

### What It's NOT:

- **Not a planning tool** - No roadmaps, no sprints, no Gantt charts
- **Not a replacement for documentation** - Issues are for execution, not strategy
- **Not heavyweight** - No Jira-style complexity

---

## Why Beads for NthLayer?

### 1. **Solves the "What should I work on next?" problem**

**Current state:**
```bash
# You manually read multiple files to find work:
$ cat docs/product/SOLO_FOUNDER_ROADMAP.md
$ cat docs/IMPROVEMENTS.md
$ grep "TODO" **/*.md
# Then mentally figure out what's blocked and what's ready
```

**With Beads:**
```bash
# Agent asks: "What's ready to work on?"
$ bd ready

📋 Ready work (3 issues):

bd-001 [P0] Fix Grafana Cloud scrape config
  No blockers, assigned to @robfox

bd-005 [P1] Generate runbook content for PostgreSQL alerts
  No blockers, ready to start

bd-012 [P2] Add Kafka technology template
  No blockers, ready to start
```

### 2. **Prevents working on blocked tasks**

**Example:**
- Task: "Build capacity planning dashboard"
- Blocker: "First need metrics collection for CPU/memory"

**With Beads:**
```bash
$ bd create "Add capacity planning dashboard" --type feature --priority P1
$ bd create "Implement metrics collection" --type task --priority P0
$ bd dep bd-002 bd-001  # bd-002 depends on bd-001

$ bd ready
# bd-002 won't show up until bd-001 is closed
```

### 3. **Tracks completion without manual updates**

**Current state:**
- Work on a feature
- Remember to update CHANGELOG.md
- Remember to move item in ROADMAP.md
- Remember to create *_COMPLETE.md file
- Remember to update README.md

**With Beads:**
```bash
$ bd create "Implement Kafka template" --type feature
# ...do the work...
$ bd close bd-003 --comment "Added Kafka alerts, dashboard panels, recording rules"
# Status automatically tracked, dependent work becomes ready
```

### 4. **Consolidates fragmented tracking**

**Current state (55 files):**
```
├── docs/IMPROVEMENTS.md (backlog)
├── docs/product/SOLO_FOUNDER_ROADMAP.md (18-month plan)
├── docs/product/OPERATIONAL_CONFIGS_EXPANSION.md (feature ideas)
├── docs/product/ERROR_BUDGETS_OPPORTUNITY.md (opportunity analysis)
├── demo/ZERO_COST_SETUP.md (deployment tasks)
├── archive/dev-notes/WEEK3_COMPLETE.md (historical tracking)
└── ...48 more files
```

**With Beads (1 file):**
```
.beads/
├── issues.jsonl  ← All issues, all dependencies
├── beads.db      ← Auto-generated query database
└── config.yaml   ← Configuration
```

All tracked in git, all queryable, all dependency-aware.

### 5. **Multi-phase work organization**

**Example: Demo deployment (current mess):**
```
demo/ZERO_COST_SETUP.md has:
- Section 1.1, 1.2, 1.3... (manual numbering)
- No way to know if 1.2 requires 1.1 completion
- No way to track which steps are done
```

**With Beads:**
```bash
$ bd create "Demo Deployment" --type epic
$ bd create "Deploy Fly.io app" --type task --depends bd-001
$ bd create "Setup Grafana Cloud" --type task --depends bd-002
$ bd create "Import dashboard" --type task --depends bd-003
$ bd create "Enable GitHub Pages" --type task --depends bd-004

$ bd list --depends bd-001  # Show entire dependency tree
$ bd ready  # Show only what's unblocked
$ bd blocked bd-005  # Show what's blocking issue 005
```

---

## Proposed Adoption Plan

### Phase 1: Initial Setup (30 minutes)

**Install Beads:**
```bash
go install github.com/steveyegge/beads/cmd/bd@latest
cd /Users/robfox/trellis
bd init
```

**Configure:**
```yaml
# .beads/config.yaml
repo_root: /Users/robfox/trellis
default_assignee: robfox
priorities: [P0, P1, P2, P3, P4]
statuses: [open, in_progress, blocked, closed]
types: [feature, bug, task, epic, doc]
```

**Commit to git:**
```bash
git add .beads/
git commit -m "Initialize beads for NthLayer project tracking"
```

### Phase 2: Migration (2-3 hours)

**Migrate existing work from markdown files:**

1. **Current work-in-progress:**
   - [x] Live demo deployment (demo/ZERO_COST_SETUP.md)
   - [ ] Grafana Cloud configuration (current blocker)

2. **Near-term roadmap (docs/product/SOLO_FOUNDER_ROADMAP.md):**
   - Month 1-3: Runbooks, capacity planning, deployment gates
   - Month 4-6: Multi-region support, cost optimization
   - Month 7-9: Backstage integration, API

3. **Feature backlog (docs/IMPROVEMENTS.md):**
   - Additional technology templates (Kafka, Elasticsearch, MongoDB)
   - Advanced alerting (anomaly detection, correlation)
   - Enhanced dashboards (SLO history, trend analysis)

**Migration script:**
```bash
# Create epics for major themes
bd create "Live Demo Infrastructure" --type epic --priority P0
bd create "Observability Suite Expansion" --type epic --priority P1
bd create "Strategic Positioning & Launch" --type epic --priority P1
bd create "Platform Expansion" --type epic --priority P2

# Create features under epics
bd create "Deploy Fly.io app" --type task --priority P0 --depends bd-001
bd create "Configure Grafana Cloud scraping" --type task --priority P0 --depends bd-002
bd create "Generate runbook content" --type feature --priority P1 --depends bd-001
bd create "Add Kafka template" --type feature --priority P2 --depends bd-001

# ...etc
```

### Phase 3: Integration with Workflow (ongoing)

**Daily workflow with AI agent:**

```bash
# Morning: What should I work on?
$ bd ready --priority P0,P1
# Shows highest priority unblocked work

# During work: Track progress
$ bd update bd-005 --status in_progress
$ bd comment bd-005 "Implemented PostgreSQL runbook, testing now"

# When blocked:
$ bd update bd-005 --status blocked
$ bd create "Need PostgreSQL test database" --type task --priority P0
$ bd dep bd-005 bd-010  # bd-005 now depends on bd-010

# When done:
$ bd close bd-005 --comment "Runbook complete, 15 procedures documented"
# Automatically unblocks dependent work

# Check project health:
$ bd stats
Open: 23 issues (P0: 3, P1: 8, P2: 12)
Ready: 5 issues
Blocked: 4 issues
In Progress: 2 issues
Closed this week: 7 issues
```

**Git integration:**
```bash
# Install git hooks (optional)
bd hooks install

# Now on every commit:
.beads/issues.jsonl automatically synced
Commit messages can reference issues: "Fix dashboard bug (bd-023)"
```

**Agent Mail integration (advanced, optional):**
```bash
# For multi-agent coordination
bd agent-mail setup
# Now multiple coding agents can coordinate via "agent mailboxes"
# Agent claims work, others see it's taken
```

### Phase 4: Cleanup (1 hour)

**Archive or consolidate markdown files:**

```bash
# Move completed tracking to archive
mv docs/**/*_COMPLETE.md archive/tracking/

# Simplify roadmap files (keep strategy, move execution to beads)
# Keep: High-level vision, market positioning, strategy
# Move to Beads: Specific features, tasks, dependencies

# Result: Cleaner repo, execution in beads, strategy in markdown
```

---

## What We Keep vs Move

### ✅ KEEP in Markdown Files

**Strategic Documentation:**
- README.md (user-facing, SEO-important)
- nthlayer_architecture.md (system design)
- docs/product/SOLO_FOUNDER_ROADMAP.md (18-month vision)
- docs/product/MESSAGING_FINAL.md (positioning)
- demo/DEMO_VALUE_PROP.md (what demo proves)

**Developer Guides:**
- GETTING_STARTED.md
- docs/DEVELOPMENT.md
- docs/CUSTOM_TEMPLATES.md

**Analysis & Research:**
- docs/product/ERROR_BUDGETS_OPPORTUNITY.md
- docs/product/AWESOME_PROMETHEUS_INTEGRATION.md

**Why:** These are narrative documents explaining "why" and "what", not "do this task"

### 🔄 MOVE to Beads

**Execution Tracking:**
- All *_COMPLETE.md files → Closed issues in beads
- IMPROVEMENTS.md → Feature issues in beads
- Task lists in demo/ZERO_COST_SETUP.md → Issues with dependencies
- "Next steps" sections in any doc → Issues

**Feature Backlog:**
- docs/product/OPERATIONAL_CONFIGS_EXPANSION.md → Epic + child issues
- Technology templates to add → Issues

**Bug Tracking:**
- Currently tracked in head/memory → Issues with type=bug

**Why:** These are actionable work items with dependencies

---

## Benefits Summary

### For You (Solo Founder)

✅ **Know what to work on next** - `bd ready` shows unblocked work  
✅ **Don't forget tasks** - Everything tracked in one place  
✅ **See project progress** - `bd stats` shows velocity  
✅ **Avoid blocked work** - Won't start something that's blocked  
✅ **Better git commits** - Reference issues: "Add Kafka template (bd-023)"  

### For AI Coding Agent

✅ **Clear work assignment** - "Here's what's ready to work on"  
✅ **Dependency awareness** - Won't work on blocked tasks  
✅ **Automatic tracking** - Agent can `bd create`, `bd update`, `bd close`  
✅ **Context in issues** - All info about a task in one place  
✅ **Multi-session memory** - Issues persist across sessions  

### For Project Management

✅ **Dependency tracking** - Know what blocks what  
✅ **Velocity measurement** - Track completion rate  
✅ **Priority enforcement** - `bd ready --priority P0` shows critical work  
✅ **Epic organization** - Group related work under epics  
✅ **Historical record** - All closed issues = project history  

---

## Risks & Mitigations

### Risk 1: Learning curve

**Mitigation:**
- Beads is simple: 10 core commands (`create`, `list`, `ready`, `close`, etc.)
- Tutorial: `bd quickstart` (interactive walkthrough)
- Can coexist with current markdown files during transition

### Risk 2: Losing narrative context

**Mitigation:**
- Keep strategic docs in markdown (vision, positioning, architecture)
- Only move execution-level tracking to beads
- Issues can have long descriptions and comments (markdown supported)

### Risk 3: Git merge conflicts

**Mitigation:**
- JSONL format is merge-friendly (one issue per line)
- SQLite DB is gitignored, auto-regenerated from JSONL
- Beads has built-in merge helpers: `bd doctor`

### Risk 4: Tool abandonment (what if beads stops being maintained?)

**Mitigation:**
- Issues are in plain text JSONL (easily parseable)
- Could write converter to GitHub Issues, Linear, etc. in 1 hour
- Can always fall back to `cat .beads/issues.jsonl | jq`

---

## Decision Framework

### Adopt Beads if:

✅ You want dependency-aware task tracking  
✅ You want "ready work" detection  
✅ You're comfortable with CLI tools  
✅ You value lightweight over feature-rich  
✅ You work with AI coding agents  

### Don't adopt if:

❌ You prefer visual kanban boards (use GitHub Projects instead)  
❌ You need team collaboration features (use Linear/Jira instead)  
❌ You want gantt charts and roadmap views  
❌ You prefer everything in markdown  

---

## Recommendation

**✅ ADOPT BEADS**

**Why:**
1. **Solves real pain:** NthLayer is too complex to track in 55 markdown files
2. **Low risk:** Can trial for 1 week, easily revert
3. **Agent-friendly:** Built specifically for AI coding workflows
4. **Proven:** 3.6k GitHub stars, active development, used by Steve Yegge himself
5. **Lightweight:** No external services, no complex setup, just git + JSONL + SQLite

**Timeline:**
- **Week 1:** Setup, migrate current work, learn commands
- **Week 2-3:** Trial period, validate it works for your workflow
- **Week 4:** Decide: commit fully or revert

**Success Metrics:**
- ✅ Can answer "what should I work on?" in <5 seconds
- ✅ Never start work on a blocked task
- ✅ Can see project velocity (issues closed per week)
- ✅ AI agent successfully uses beads to track work
- ✅ Reduced cognitive load (fewer files to mentally track)

---

## Example Migration: Live Demo Infrastructure

**Current state (demo/ZERO_COST_SETUP.md):**

```markdown
## Step 1: Setup Fly.io (30 minutes)
1.1 Create account
1.2 Install CLI
1.3 Deploy app
1.4 Configure secrets

## Step 2: Setup Grafana Cloud (30 minutes)
2.1 Create account
2.2 Add scrape config  ← YOU ARE HERE (BLOCKED)
2.3 Verify metrics
...
```

**With Beads:**

```bash
$ bd list --epic "Live Demo"

Epic: Live Demo Infrastructure (bd-001) [OPEN]
├─ bd-002 [CLOSED] Setup Fly.io account
├─ bd-003 [CLOSED] Deploy Fly.io app
├─ bd-004 [CLOSED] Configure Fly.io secrets
├─ bd-005 [OPEN] Configure Grafana Cloud scraping ← IN PROGRESS
│  └─ depends on: bd-004 (closed) ✓
├─ bd-006 [BLOCKED] Verify metrics flowing
│  └─ depends on: bd-005 (open) ⏳
├─ bd-007 [BLOCKED] Import NthLayer dashboard
│  └─ depends on: bd-006 (blocked) ⏳
└─ bd-008 [BLOCKED] Enable GitHub Pages
   └─ depends on: bd-007 (blocked) ⏳

$ bd show bd-005
ID: bd-005
Title: Configure Grafana Cloud scraping
Status: in_progress
Priority: P0
Type: task
Assignee: robfox
Created: 2025-12-01 14:23:45
Updated: 2025-12-01 16:45:12

Description:
Add scrape job to Grafana Cloud to pull metrics from Fly.io app.
Endpoint: https://nthlayer-demo.fly.dev/metrics
Need explicit steps to configure Prometheus scrape.

Comments:
[2025-12-01 16:45] App is deployed and metrics endpoint working
[2025-12-01 16:50] Working on Grafana Cloud configuration now

Dependencies:
Depends on: bd-004 (Configure Fly.io secrets) [CLOSED]
Blocks: bd-006 (Verify metrics flowing)

$ bd ready
bd-005: Configure Grafana Cloud scraping [P0]
  └─ All blockers resolved, ready to work
```

**Much clearer than scrolling through markdown!**

---

## Next Steps

1. **Decision:** Do you want to adopt beads? (Yes/No/Trial)

2. **If YES/Trial:**
   - [ ] Install beads: `go install github.com/steveyegge/beads/cmd/bd@latest`
   - [ ] Initialize: `bd init` in trellis directory
   - [ ] Create first issue: `bd create "Configure Grafana Cloud scraping" --type task --priority P0`
   - [ ] Test workflow for 1 week

3. **If NO:**
   - Alternative: Consolidate markdown files into fewer tracking docs
   - Alternative: Use GitHub Issues/Projects for tracking
   - Keep current system, accept fragmentation

---

## Appendix: Beads Quick Reference

### Core Commands

```bash
# Create issues
bd create "Issue title" --type feature --priority P1
bd create "Bug fix" --type bug --priority P0 --assignee robfox

# List issues
bd list                    # All open issues
bd list --priority P0      # Only P0 issues
bd list --status closed    # Closed issues
bd list --assignee robfox  # My issues

# Find ready work
bd ready                   # All unblocked issues
bd ready --priority P0,P1  # High priority only

# Update issues
bd update bd-005 --status in_progress
bd comment bd-005 "Working on this now"
bd close bd-005 --comment "Done!"

# Dependencies
bd dep bd-002 bd-001       # bd-002 depends on bd-001
bd blocked bd-002          # What's blocking bd-002?
bd blocks bd-001           # What does bd-001 block?

# Project health
bd stats                   # Overall statistics
bd stats --assignee robfox # My stats

# Details
bd show bd-005             # Full issue details
bd tree bd-001             # Dependency tree for epic
```

### Issue Types

- **epic** - Large multi-issue effort
- **feature** - New functionality
- **bug** - Something broken
- **task** - Specific work item
- **doc** - Documentation work

### Priorities

- **P0** - Critical (blocking launch, production down)
- **P1** - High (important features, major bugs)
- **P2** - Medium (nice-to-have features)
- **P3** - Low (polish, minor improvements)
- **P4** - Nice-to-have (someday/maybe)

### Statuses

- **open** - Not started, ready to work
- **in_progress** - Currently working on it
- **blocked** - Waiting on dependency or external factor
- **closed** - Done!

---

**Status:** Ready for decision  
**Decision Maker:** @robfox  
**Expected Timeline:** Week 1: Setup & trial, Week 2-3: Evaluate, Week 4: Commit or revert
