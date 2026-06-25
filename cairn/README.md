# Cairn

> *A cairn is a stack of stones that marks a trail — and remembers the path you
> took. This plugin does the same for a project: it stacks **plan → work →
> memory** into one marker so a solo build stays on-trail.*

A Claude Code plugin that wires the [GSD](https://github.com/) planning
workflow (`/gsd:*`, `.planning/`) to the [beads](https://github.com/gastownhall/beads)
issue tracker (`bd`, `.beads/`) so phase planning and execution **create,
claim, and close** tracked work automatically — and optionally makes the
[context-mode](https://github.com/mksglu/context-mode) knowledge base
**intent-aware**, scoping compressed memory to the active issue and phase.

It is **thin glue** — it does not fork, vendor, or modify GSD, beads, or
context-mode. They stay independent upstream dependencies; Cairn only ships the
conventions that connect them.

## What it does

When a repo contains **both** `.planning/` (GSD) and `.beads/` (beads):

- **Phase ↔ issues** — each GSD phase `NN` maps requirement IDs → bd issue IDs
  in `.planning/phases/NN-<slug>/NN-BEADS-MAP.md`.
- **Labels** — every bd issue for phase `N` carries `phase-N` (`bd list -l phase-N`).
- **Plan frontmatter** — each `PLAN.md` carries `beads: [ids]` it advances.
- **Lifecycle** — `new-project` creates issues, `plan-phase` reads the map and
  sets frontmatter, `execute-phase` claims → in_progress → closes, `ship`
  verifies all closed before push.
- **Precedence** — GSD phase docs win over conflicting bd issue text.

It activates **only** when both directories are present, so it's silent in
non-GSD or non-beads repos.

## Requirements

- [GSD](https://github.com/) installed (provides `/gsd:*`)
- [beads](https://github.com/gastownhall/beads) installed (`bd` on PATH)

## Install

```text
/plugin marketplace add BigJiggity/claude-plugins
/plugin install cairn@claude-plugins
```

## Use

```text
/cairn:init        # bootstrap: git + bd init in the current repo
/gsd:new-project       # then create .planning/ + ROADMAP
```

After both `.planning/` and `.beads/` exist, every `/gsd:*` command follows the
integration convention (see the bundled `cairn` skill).

## Two-way sync to external tools (optional)

Mirror bd issues to **GitHub Issues, GitLab, Jira, Asana, and/or Azure Boards** —
**hub-and-spoke, pull-on-demand**. bd is the hub and source of truth; every tool
syncs to bd, never tool-to-tool.

- **PUSH** (bd → tools): fires on bd lifecycle events (create / claim / close).
- **PULL** (tools → bd): `/cairn:sync-pull` reconciles external edits back
  into bd with **last-writer-wins by timestamp**; genuine both-sides-changed
  cases are logged to `.cairn/conflicts.json`.

Setup:

```text
/cairn:sync-config     # pick backends, write .cairn/sync.json
# export the API tokens it tells you to (tokens are referenced by ENV VAR NAME,
# never stored in the repo)
/cairn:sync-pull       # reconcile external edits into bd, on demand
```

Each tool is a small **adapter** in `adapters/` implementing a simple
stdin/stdout contract (`adapters/_contract.md`). Add another tool (Linear,
Trello, …) by dropping in one adapter and a `sync.json` block — no dispatcher
changes. Adapters read API tokens from environment variables named in
`sync.json`; **no secrets are ever written to disk**.

> GitHub is live-tested (via the `gh` CLI's auth). GitLab / Jira / Asana /
> Azure Boards adapters are implemented to each tool's REST spec; supply the
> relevant API token env var to use them.

**📖 Full guide:** [`docs/sync.md`](./docs/sync.md) — architecture, data model,
the reconciliation algorithm, per-backend setup, the adapter contract, security,
and troubleshooting.

## Intent-aware memory (context-mode integration, optional)

If you also run the [context-mode](https://github.com/mksglu/context-mode)
plugin, this gives its knowledge base **architectural awareness**. context-mode
compresses runtime data well but is blind to *what the work is*; this layer ties
its memory to the **active bd issue** and **GSD phase**:

- **Scope by intent** — index during execution under a `source` label
  `gb/<bd_id>/<phase>`, then recall scoped to the active task
  (`ctx_search(source: "<bd_id>")`) instead of the whole session's noise.
- **Phase-driven scope switch** — on `Execute → Verify`, checkpoint `ctx_stats`
  and switch the active scope to the new phase's label; the prior phase's noise
  is simply no longer searched.
- **Capacity guard** — when `ctx_stats` token usage crosses a configurable
  threshold, the agent is told to split the active bd issue into sub-tasks
  (`bd create` + `bd dep add`) — a natural context reset before the window degrades.

**Scope-by-label only** — this layer never deletes the knowledge base.
context-mode can only purge by whole session or whole project, so any real wipe
(`ctx_purge`) stays a manual, user-confirmed action.

Setup:

```text
/cairn:context-config   # opt in, write .cairn/context.json, tune the threshold
```

The `cairn-context` skill activates once that config exists and the `ctx_*`
tools are available.

**📖 Full guide:** [`docs/context.md`](./docs/context.md) — the layered model,
the source-label convention, the three behaviors, configuration, capability
boundaries, and troubleshooting.

## Components

| Path | Purpose |
|---|---|
| `skills/cairn/SKILL.md` | the GSD↔bd integration convention |
| `skills/cairn-sync/SKILL.md` | the bd↔external-tools sync convention |
| `skills/cairn-context/SKILL.md` | the context-mode intent-aware memory convention |
| `commands/init.md` | `/cairn:init` — bootstrap a repo (git + bd init) |
| `commands/sync-config.md` | `/cairn:sync-config` — configure backends |
| `commands/sync-pull.md` | `/cairn:sync-pull` — reconcile tools → bd |
| `commands/context-config.md` | `/cairn:context-config` — opt into context-mode integration |
| `scripts/gbsync.py` · `gbsync.sh` | the push/pull sync dispatcher |
| `adapters/*.py` | github · gitlab · jira · asana · azure-boards adapters |
| `adapters/_contract.md` | the adapter interface spec |
| `hooks/session-start.sh` | "integration active" reminder when both dirs present |
| `scripts/cairn-init.sh` | the bootstrap script (git + bd init) |
| `templates/sync.json.example` | starter sync config |
| `templates/context.json.example` | starter context-mode config |

## Privacy

`cairn` runs entirely on your machine, collects no telemetry, and sends data
only to the external trackers you explicitly enable (using your own
credentials). See [`PRIVACY.md`](./PRIVACY.md).

## License

MIT
