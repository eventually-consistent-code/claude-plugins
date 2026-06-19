# Privacy Policy — gsd-beads

_Last updated: 2026-06-19_

`gsd-beads` is an open-source Claude Code plugin. It runs **entirely on your own
machine**. The author operates no servers, collects no telemetry, and receives
no data from your use of the plugin.

## What the plugin does with data

- **Runs locally.** All logic (the dispatcher, hooks, and adapters) executes on
  your machine within your own repository. There is no "gsd-beads service."
- **No collection by the author.** The plugin sends nothing to the author or any
  author-controlled endpoint. There is no analytics, tracking, or phone-home.

## Data sent to third parties (only the ones you enable)

When you configure and enable a backend in `.gsd-beads/sync.json`, the plugin
transmits issue data **to that external service, using your own credentials**, so
your `bd` (Beads) issues can be mirrored there. Specifically:

- **What is sent:** the fields needed to create/update/close the mirrored item —
  issue title, description/body, status, labels, and the external item's ID.
- **Where it is sent:** only to the services you explicitly enable, e.g. GitHub,
  GitLab, Jira, Asana, and/or Azure Boards.
- **Pull direction:** when you run a reconcile, the plugin reads the current
  state of mapped items back from those same services.

Each enabled service processes that data under **its own privacy policy and
terms** — GitHub, GitLab, Atlassian (Jira), Asana, and Microsoft (Azure DevOps)
respectively. Review theirs for how they handle the data you mirror.

If you enable **no** backends, the plugin sends no data anywhere.

## Credentials and secrets

- API tokens are read from **environment variables** whose *names* you put in
  `sync.json`. The plugin never stores token values on disk and never transmits
  them anywhere except, over HTTPS, to the corresponding service's API to
  authenticate your own requests.
- The GitHub adapter uses your existing `gh` CLI authentication.
- `sync.json` (committed) contains configuration and env-var *names* only — no
  secrets. Keep your tokens in your environment / secret manager.

## Local files

The plugin reads and writes files inside your repository: `.beads/`,
`.planning/`, and `.gsd-beads/` (`id-map.json`, `state.json`, `conflicts.json`).
These stay in your working tree under your control. The generated state files are
gitignored by default; whether to commit them is your choice.

## Changes

This policy may change as the plugin evolves. Material changes will be reflected
in this file in the repository, with an updated date above.

## Contact

Questions or concerns: open an issue at
<https://github.com/BigJiggity/claude-plugins/issues>.
