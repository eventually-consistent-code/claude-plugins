# gsd-beads

A Claude Code plugin that wires the [GSD](https://github.com/) planning
workflow (`/gsd:*`, `.planning/`) to the [beads](https://github.com/gastownhall/beads)
issue tracker (`bd`, `.beads/`) so phase planning and execution **create,
claim, and close** tracked work automatically.

It is **thin glue** — it does not fork, vendor, or modify GSD or beads. Both
stay independent upstream dependencies; this plugin only ships the convention
that connects them.

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
/plugin install gsd-beads@claude-plugins
```

## Use

```text
/gsd-beads:init        # bootstrap: git + bd init in the current repo
/gsd:new-project       # then create .planning/ + ROADMAP
```

After both `.planning/` and `.beads/` exist, every `/gsd:*` command follows the
integration convention (see the bundled `gsd-beads` skill).

## Two-way sync to external tools (optional)

Mirror bd issues to **GitHub Issues, GitLab, Jira, Asana, and/or Azure Boards** —
**hub-and-spoke, pull-on-demand**. bd is the hub and source of truth; every tool
syncs to bd, never tool-to-tool.

- **PUSH** (bd → tools): fires on bd lifecycle events (create / claim / close).
- **PULL** (tools → bd): `/gsd-beads:sync-pull` reconciles external edits back
  into bd with **last-writer-wins by timestamp**; genuine both-sides-changed
  cases are logged to `.gsd-beads/conflicts.json`.

Setup:

```text
/gsd-beads:sync-config     # pick backends, write .gsd-beads/sync.json
# export the API tokens it tells you to (tokens are referenced by ENV VAR NAME,
# never stored in the repo)
/gsd-beads:sync-pull       # reconcile external edits into bd, on demand
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

## Components

| Path | Purpose |
|---|---|
| `skills/gsd-beads/SKILL.md` | the GSD↔bd integration convention |
| `skills/gsd-beads-sync/SKILL.md` | the bd↔external-tools sync convention |
| `commands/init.md` | `/gsd-beads:init` — bootstrap a repo (git + bd init) |
| `commands/sync-config.md` | `/gsd-beads:sync-config` — configure backends |
| `commands/sync-pull.md` | `/gsd-beads:sync-pull` — reconcile tools → bd |
| `scripts/gbsync.py` · `gbsync.sh` | the push/pull sync dispatcher |
| `adapters/*.py` | github · gitlab · jira · asana · azure-boards adapters |
| `adapters/_contract.md` | the adapter interface spec |
| `hooks/session-start.sh` | "integration active" reminder when both dirs present |
| `scripts/gsd-beads-init.sh` | the bootstrap script (git + bd init) |
| `templates/sync.json.example` | starter sync config |

## Privacy

`gsd-beads` runs entirely on your machine, collects no telemetry, and sends data
only to the external trackers you explicitly enable (using your own
credentials). See [`PRIVACY.md`](./PRIVACY.md).

## License

MIT
