#!/usr/bin/env bash
# cairn SessionStart hook.
# Only emits context when the project uses BOTH GSD and beads.
# Anything printed to stdout is injected into the session as additional context.
set -euo pipefail

# Resolve project dir: prefer the hook payload's cwd, fall back to $PWD.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

if [ -d "$PROJECT_DIR/.planning" ] && [ -d "$PROJECT_DIR/.beads" ]; then
  cat <<'MSG'
[cairn] This repo uses BOTH GSD (.planning/) and beads (.beads/).
The cairn integration is active — use the `cairn` skill conventions:
  • each phase NN maps requirements -> bd ids in .planning/phases/NN-*/NN-BEADS-MAP.md
  • every bd issue carries label phase-N ; list with: bd list -l phase-N
  • every PLAN.md carries a `beads:` frontmatter list of the bd ids it advances
  • execute-phase: claim -> in_progress -> close each plan's bd ids
  • on conflict, GSD phase docs (CONTEXT/PLAN/ROADMAP) win over bd issue text
  • use `bd` for ALL task tracking (not TodoWrite / markdown TODOs)
Run `bd prime` for the full bd command reference and session-close protocol.
MSG

  # Context-mode integration is opt-in: only emit when the repo has the config.
  if [ -f "$PROJECT_DIR/.cairn/context.json" ]; then
    cat <<'MSG'
[cairn] context-mode integration is enabled (.cairn/context.json).
Use the `cairn-context` skill conventions when the ctx_* tools are present:
  • index during execution under source label gb/<bd_id>/<phase>
  • recall scoped to the active task: ctx_search(source: "<bd_id>")
  • stream logs/test output via ctx_execute_file (don't persist them)
  • on phase transition: ctx_stats checkpoint, switch scope to the new phase label
  • capacity guard: if ctx_stats tokens exceed the configured threshold, advise
    splitting the active bd issue into sub-tasks (bd create + bd dep add)
  • scope-by-label only — this layer NEVER calls ctx_purge (manual/user-only)
MSG
  fi
fi

exit 0
