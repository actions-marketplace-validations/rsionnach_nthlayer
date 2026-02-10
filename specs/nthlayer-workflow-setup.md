# NthLayer Workflow Setup Specification

## Overview

This spec defines five workflow improvements to be installed in this repo. Read this entire document in plan mode first, present your plan, then implement only after approval.

**Important:** Do NOT modify any existing NthLayer source code, tests, or configuration. This spec only touches `.claude/`, `CLAUDE.md`, and project-level Claude Code configuration. If Beads is not already initialised in this repo, run `bd init` first.

---

## 1. Install claude-code-auto-memory plugin

**What:** Install the `severity1/claude-code-auto-memory` plugin to automatically maintain CLAUDE.md sections based on what Claude learns during sessions.

**Steps:**
1. Install via the plugin marketplace: `/plugin install severity1/claude-code-auto-memory`
2. If that's unavailable, install from GitHub: `/install-github-plugin severity1/claude-code-auto-memory`
3. Verify it creates PostToolUse hooks in the settings
4. Add auto-managed section markers to CLAUDE.md (see section 6 below)

**Acceptance criteria:**
- Plugin is installed and visible in `/plugin list`
- PostToolUse hooks are registered in `.claude/settings.json`
- CLAUDE.md has `<!-- AUTO-MANAGED: learned-patterns -->` and `<!-- AUTO-MANAGED: discovered-conventions -->` section markers

---

## 2. SessionStart hook — context injection

**What:** A SessionStart hook that automatically injects Beads state, recent spec changes, and current project context at the start of every session.

**Create file:** `.claude/hooks/session-start.sh`

**Behaviour:**
```
#!/usr/bin/env bash
set -euo pipefail

echo "## Current Beads State"
echo ""

# Show ready work
if command -v bd &>/dev/null; then
    READY=$(bd ready --json 2>/dev/null || echo "[]")
    COUNT=$(echo "$READY" | jq 'length' 2>/dev/null || echo "0")
    echo "**Ready tasks:** $COUNT"
    if [ "$COUNT" -gt 0 ]; then
        echo ""
        echo "$READY" | jq -r '.[] | "- [\(.id)] \(.title) (P\(.priority // "?"))"' 2>/dev/null || true
    fi
    echo ""

    # Show in-progress work
    IN_PROGRESS=$(bd list --status in_progress --json 2>/dev/null || echo "[]")
    IP_COUNT=$(echo "$IN_PROGRESS" | jq 'length' 2>/dev/null || echo "0")
    if [ "$IP_COUNT" -gt 0 ]; then
        echo "**In progress:** $IP_COUNT"
        echo "$IN_PROGRESS" | jq -r '.[] | "- [\(.id)] \(.title)"' 2>/dev/null || true
        echo ""
    fi
else
    echo "⚠ Beads (bd) not found in PATH"
    echo ""
fi

# Show recent spec changes
echo "## Recent Spec Changes"
echo ""
SPEC_CHANGES=$(git diff --name-only HEAD~10 -- specs/ docs/specs/ spec/ 2>/dev/null || echo "")
if [ -n "$SPEC_CHANGES" ]; then
    echo "$SPEC_CHANGES" | while read -r f; do echo "- $f"; done
else
    echo "No spec changes in last 10 commits."
fi
echo ""

# Show uncommitted changes as a reminder
DIRTY=$(git status --porcelain 2>/dev/null | head -10)
if [ -n "$DIRTY" ]; then
    echo "## ⚠ Uncommitted Changes"
    echo ""
    echo "$DIRTY"
    echo ""
fi
```

**Register in `.claude/settings.json`:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

**Acceptance criteria:**
- `.claude/hooks/session-start.sh` exists and is executable (`chmod +x`)
- Hook is registered in `.claude/settings.json` under `SessionStart`
- Running `bash .claude/hooks/session-start.sh` manually produces output showing beads state and spec changes without errors

---

## 3. Stop hook — "land the plane" enforcement

**What:** A Stop hook that prevents Claude from voluntarily ending a session if there are uncommitted changes or Beads issues that haven't been updated. Returns exit code 2 (which blocks the stop and reinjects the message as a prompt) when cleanup is incomplete.

**Create file:** `.claude/hooks/stop-check.sh`

**Behaviour:**
```
#!/usr/bin/env bash
set -euo pipefail

ISSUES=""

# Check for uncommitted changes
if ! git diff --quiet 2>/dev/null; then
    ISSUES="${ISSUES}• You have uncommitted changes. Please commit or stash before ending the session.\n"
fi

# Check for staged but uncommitted changes
if ! git diff --cached --quiet 2>/dev/null; then
    ISSUES="${ISSUES}• You have staged changes that haven't been committed.\n"
fi

# Check if there are in-progress beads that should be updated
if command -v bd &>/dev/null; then
    IN_PROGRESS=$(bd list --status in_progress --json 2>/dev/null || echo "[]")
    IP_COUNT=$(echo "$IN_PROGRESS" | jq 'length' 2>/dev/null || echo "0")
    if [ "$IP_COUNT" -gt 0 ]; then
        ISSUES="${ISSUES}• There are $IP_COUNT in-progress beads. Update their status or file remaining work before ending.\n"
    fi
fi

# Check for unpushed commits
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNPUSHED" -gt 0 ]; then
    ISSUES="${ISSUES}• You have $UNPUSHED unpushed commit(s). Run git push before ending.\n"
fi

if [ -n "$ISSUES" ]; then
    echo "## Land the Plane 🛬"
    echo ""
    echo "Cannot end session — cleanup required:"
    echo ""
    echo -e "$ISSUES"
    echo ""
    echo "Please complete cleanup, then try again."
    exit 2  # Blocks stop, reinjects this message
fi

# All clear
exit 0
```

**Register in `.claude/settings.json`** (merge with existing hooks):
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/stop-check.sh"
          }
        ]
      }
    ]
  }
}
```

**Acceptance criteria:**
- `.claude/hooks/stop-check.sh` exists and is executable
- Hook is registered under `Stop` in `.claude/settings.json`
- With dirty git state, running the script returns exit code 2
- With clean git state and no in-progress beads, returns exit code 0
- Script handles missing `bd` command gracefully (skips beads checks)

---

## 4. Spec-to-Beads slash command

**What:** A slash command that reads a specification document and decomposes it into a Beads epic with dependency-aware tasks.

**Create file:** `.claude/commands/spec-to-beads.md`

**Content:**
```markdown
---
description: Decompose a specification into Beads issues with dependency tracking
allowed-tools: Bash, Read, Write, Task
---

# Spec-to-Beads: $ARGUMENTS

Read the specification file provided in $ARGUMENTS (e.g., `/spec-to-beads specs/feature-x.md`).

## Instructions

### Phase 1: Analyse the spec
1. Read the entire spec file
2. Identify:
   - The overall feature/epic name
   - Discrete implementation tasks (aim for tasks that take 15-60 minutes each)
   - Dependencies between tasks (what must be done before what)
   - Acceptance criteria for each task
   - Any design decisions or constraints noted in the spec

### Phase 2: Create the epic
1. Create a Beads epic for the overall feature:
   ```
   bd create "<epic-name>" --type epic --priority 1 --description "<one-line summary from spec>"
   ```
2. Note the epic ID returned

### Phase 3: Create tasks with dependencies
For each task identified, create a Beads issue:
```
bd create "<task-title>" --type task --priority <1-3> --description "<what to implement>" --notes "Spec: $ARGUMENTS | Acceptance: <criteria>"
```

Then add dependency links:
```
bd update <task-id> --blocked-by <dependency-id>
```

Link each task to the epic:
```
bd update <task-id> --parent <epic-id>
```

### Phase 4: Verify
1. Run `bd list --epic <epic-id>` to show all created tasks
2. Run `bd ready` to confirm the dependency graph is valid and the first tasks are unblocked
3. Present a summary table:
   - Task ID | Title | Priority | Blocked by | Status

### Rules
- Tasks should be atomic — one clear deliverable per task
- Always set `--priority` (1 = must have, 2 = should have, 3 = nice to have)
- Include the spec file path in the `--notes` field of every task for traceability
- If the spec references other specs or ADRs, note those in the task description
- Do NOT begin implementation — this command only creates the task graph
```

**Acceptance criteria:**
- `.claude/commands/spec-to-beads.md` exists
- `/project:spec-to-beads specs/example.md` is autocomplete-discoverable in Claude Code
- The command creates a Beads epic with linked, dependency-ordered tasks
- Each task includes a reference back to the source spec file

---

## 5. Ralph Wiggum loop prompt file

**What:** A reusable prompt file for running NthLayer development in a Ralph Wiggum autonomous loop with Beads as the task queue.

**Create file:** `.claude/ralph-prompt.md`

**Content:**
```markdown
# NthLayer Autonomous Development Loop

You are working on the NthLayer project. Your task execution follows this exact cycle:

## Step 1: Orient
- Read CLAUDE.md for project context and conventions
- Run `bd ready --json` to find the highest-priority unblocked task
- If no tasks are ready, output "RALPH_COMPLETE" and stop

## Step 2: Claim
- Run `bd update <task-id> --status in_progress`
- Read the task description, notes, and any linked spec files

## Step 3: Implement
- Implement the task following all conventions in CLAUDE.md
- Write or update tests for any changed functionality
- Run the project's test suite to verify nothing is broken

## Step 4: Verify
- Run tests: ensure all pass
- Run linting/formatting if configured
- If tests fail, fix the issues before proceeding

## Step 5: Complete
- Run `bd update <task-id> --status closed`
- Commit with a descriptive message referencing the bead ID: `git commit -m "feat: <description> [<bead-id>]"`
- If you discovered new work during implementation, file it: `bd create "<new-task>" --type task --priority 2`

## Step 6: Continue or finish
- Run `bd ready --json` again
- If more tasks exist, return to Step 2
- If no tasks remain, run `git push`, then output "RALPH_COMPLETE"

## Rules
- Never skip tests
- Never mark a task closed if tests are failing
- If stuck on a task for more than 3 attempts, file a bug bead and move to the next ready task
- Always commit after each completed task — small, atomic commits
- The completion promise is: RALPH_COMPLETE
```

**Also create:** `.claude/ralph-loop.sh`

```bash
#!/usr/bin/env bash
# NthLayer Ralph Wiggum loop
# Usage: .claude/ralph-loop.sh [max-iterations]

set -euo pipefail

MAX_ITERATIONS=${1:-20}
PROMPT_FILE=".claude/ralph-prompt.md"
ITERATION=0

echo "🔁 Starting NthLayer Ralph loop (max $MAX_ITERATIONS iterations)"
echo ""

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo "--- Iteration $ITERATION / $MAX_ITERATIONS ---"

    OUTPUT=$(claude -p "$(cat $PROMPT_FILE)" --allowedTools 'Bash(git*),Bash(bd*),Bash(npm*),Bash(node*),Read,Write,Task' 2>&1)

    echo "$OUTPUT" | tail -5

    if echo "$OUTPUT" | grep -q "RALPH_COMPLETE"; then
        echo ""
        echo "✅ Ralph loop complete after $ITERATION iteration(s)"
        exit 0
    fi
done

echo ""
echo "⚠ Reached max iterations ($MAX_ITERATIONS). Check bd list for remaining work."
exit 1
```

**Acceptance criteria:**
- `.claude/ralph-prompt.md` exists
- `.claude/ralph-loop.sh` exists and is executable
- The loop script can be invoked with `.claude/ralph-loop.sh 5` (dry run with low iteration count)
- The prompt references `RALPH_COMPLETE` as the completion promise

---

## 6. CLAUDE.md updates

**What:** Update the project's CLAUDE.md to reference the new workflow tooling. Add the following sections, preserving all existing content.

**Append to CLAUDE.md:**

```markdown

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
```

**Acceptance criteria:**
- CLAUDE.md contains the workflow tooling section
- Auto-managed markers are present for the auto-memory plugin
- No existing CLAUDE.md content has been removed or modified

---

## Implementation order

1. Ensure Beads is initialised (`bd init` if needed)
2. Create `.claude/hooks/` directory
3. Create and register SessionStart hook (section 2)
4. Create and register Stop hook (section 3)
5. Create spec-to-beads slash command (section 4)
6. Create Ralph loop files (section 5)
7. Update CLAUDE.md (section 6)
8. Install auto-memory plugin (section 1)
9. Commit all changes: `git commit -m "chore: add workflow tooling (hooks, commands, ralph loop)"`
10. Verify: start a new Claude Code session and confirm SessionStart hook fires

## What NOT to do
- Do not modify any NthLayer source code, tests, or build configuration
- Do not modify any existing Beads issues
- Do not run the Ralph loop — only create the files
- Do not install any npm/pip packages into the project
- If the project already has a `.claude/settings.json`, merge hooks into it — do not overwrite
