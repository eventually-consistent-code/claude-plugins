#!/usr/bin/env bash
# cairn-init — bootstrap a project for the GSD<->beads integration.
# Ensures git + beads are live so the cairn skill/hook activates.
# GSD's own .planning/ is created interactively by /gsd:new-project inside Claude.
#
# Usage:  cairn-init.sh [target-dir]   (defaults to current dir)
set -euo pipefail

DIR="${1:-$PWD}"
cd "$DIR"
echo "▸ bootstrapping GSD<->beads in: $DIR"

# 1. git repo
if [ -d .git ]; then
  echo "  ✓ git repo already present"
else
  git init -q
  echo "  ✓ git init"
fi

# 2. beads
if ! command -v bd >/dev/null 2>&1; then
  echo "  ✗ 'bd' not on PATH — install beads first (https://github.com/gastownhall/beads)" >&2
  exit 1
fi
if [ -d .beads ]; then
  echo "  ✓ .beads/ already present"
else
  bd init
  echo "  ✓ bd init"
fi

cat <<'NEXT'

▸ next steps (inside Claude Code):
    1. /gsd:new-project        # creates .planning/ + ROADMAP, then create one bd issue per requirement
    2. /gsd:plan-phase 1       # reads NN-BEADS-MAP.md, sets beads: frontmatter
    3. /gsd:execute-phase 1    # claim -> in_progress -> close per plan

  (.planning/ is created by step 1 — this script only wires git + beads.)
  The cairn skill activates once both .planning/ and .beads/ exist.
NEXT
