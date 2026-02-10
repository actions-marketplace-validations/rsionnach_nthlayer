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
