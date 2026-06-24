---
description: Enable/configure the context-mode integration (intent-aware memory) — writes .gsd-beads/context.json
---

Opt this repo into the gsd-beads ↔ context-mode integration, which scopes
context-mode's knowledge base by the active bd issue + GSD phase and watches
token usage to advise task-splitting. Do the following:

1. Confirm prerequisites:
   - `.beads/` exists (`ls .beads/`). If not, tell the user to run
     `/gsd-beads:init` first and stop.
   - The `ctx_*` MCP tools (context-mode) are available this session. If not,
     tell the user to install the **context-mode** plugin first and stop —
     without it this integration does nothing.

2. If `.gsd-beads/context.json` does not exist, create `.gsd-beads/` and seed it
   from the template:
   ```bash
   mkdir -p .gsd-beads
   cp "${CLAUDE_PLUGIN_ROOT}/templates/context.json.example" .gsd-beads/context.json
   ```
   If it already exists, read it and edit in place (preserve existing values).

3. Ask the user (AskUserQuestion) to tune two things:
   - **Capacity guard** — keep it on? If yes, set `capacity_guard.token_threshold`
     to match their autonomous-loop length:
     short single-phase ≈ `80000`, medium multi-phase ≈ `150000` (default),
     long autonomous ≈ `300000`. If off, set `capacity_guard.enabled: false`.
   - **Source template** — keep the default `gb/{bd_id}/{phase}` unless they
     want a different label scheme. `{bd_id}` and `{phase}` are the only
     interpolated fields.

4. Leave `reset.mode` as `scope-by-label`. Explain that this integration never
   deletes the knowledge base — `ctx_purge` (session or whole project) stays a
   manual, user-confirmed action. Do not offer an auto-purge mode; context-mode
   has no per-phase or per-task delete.

5. Confirm what you wrote (path + the values set) and point the user at the
   `gsd-beads-context` skill, which activates automatically now that the config
   exists.
