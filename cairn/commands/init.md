---
description: Bootstrap the current repo for the GSD↔beads integration (git + bd init), then guide the GSD project setup
---

Bootstrap the current working directory so the `cairn` integration
activates. Do the following:

1. Run the bootstrap script:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/cairn-init.sh" "$PWD"
   ```
   It ensures the directory is a git repo and runs `bd init` if `.beads/` is
   missing. It will error if `bd` is not installed — if so, tell the user to
   install beads (https://github.com/gastownhall/beads) and stop.

2. Report what it did (git initialized?, beads initialized?).

3. Tell the user the remaining steps must run inside Claude:
   - `/gsd:new-project` to create `.planning/` and the ROADMAP. After the
     roadmap exists, follow the `cairn` skill: create one bd issue per
     requirement, label each `phase-N`, and write each `NN-BEADS-MAP.md`.
   - Then `/gsd:plan-phase 1`, `/gsd:execute-phase 1`, etc.

4. Note: the `cairn` skill keys off both `.planning/` and `.beads/` being
   present. `.planning/` is created by `/gsd:new-project`, so full wiring is
   active once both exist.

Do NOT create `.planning/` yourself — that is `/gsd:new-project`'s job.
