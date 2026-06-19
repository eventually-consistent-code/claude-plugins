---
description: Configure two-way bd↔external sync (GitHub/GitLab/Jira/Asana/Azure Boards) — writes .gsd-beads/sync.json
---

Set up the gsd-beads sync backends for this repo. bd is the hub/source of
truth; tools sync to bd (hub-and-spoke). Do the following:

1. Confirm prerequisites: the repo has `.beads/` (run `ls .beads/`). If not,
   tell the user to run `/gsd-beads:init` first and stop.

2. If `.gsd-beads/sync.json` does not exist, create `.gsd-beads/` and seed it
   from the template:
   ```bash
   mkdir -p .gsd-beads
   cp "${CLAUDE_PLUGIN_ROOT}/templates/sync.json.example" .gsd-beads/sync.json
   ```
   If it already exists, read it and edit in place (preserve existing values).

3. Ask the user (AskUserQuestion) which backends to enable: **GitHub**,
   **GitLab**, **Jira**, **Asana**, **Azure Boards** (multiSelect). For each
   chosen backend, collect the required `config` fields and set `"enabled": true`:
   - **github**: `repo` (owner/name). Uses the `gh` CLI's existing auth — no token field.
   - **gitlab**: `project` (numeric id or `namespace/project`), `base_url`
     (default `https://gitlab.com`; set for self-hosted), and ENV VAR NAME `token_env`.
   - **jira**: `base_url`, `project_key`, `issue_type`, and the ENV VAR NAMES
     `email_env` / `token_env`, plus `transitions.in_progress` / `transitions.closed`.
   - **asana**: `project_gid` and ENV VAR NAME `token_env`.
   - **azure-boards**: `org_url`, `project`, `work_item_type`, ENV VAR NAME
     `pat_env`, and `states.in_progress` / `states.closed` (match the project's
     process template).

4. **Secrets rule:** write only ENV VAR NAMES into `sync.json`, never token
   values. After saving, tell the user exactly which env vars to export
   (e.g. `export JIRA_API_TOKEN=…`) and where to mint each credential:
   - GitLab token (`api` scope): https://gitlab.com/-/user_settings/personal_access_tokens
   - Jira token: https://id.atlassian.com/manage-profile/security/api-tokens
   - Asana PAT: https://app.asana.com/0/my-apps
   - Azure DevOps PAT (Work Items Read & Write): `https://dev.azure.com/<org>/_usersSettings/tokens`
   - GitHub: `gh auth status` (no separate token needed)

5. Add `.gsd-beads/id-map.json`, `.gsd-beads/state.json`, and
   `.gsd-beads/conflicts.json` are generated at sync time. `sync.json` is meant
   to be committed; the others may be committed or gitignored per the user's
   preference — ask.

6. Tell the user how to drive it:
   - PUSH happens automatically during the `gsd-beads-sync` lifecycle, or
     manually: `bash "${CLAUDE_PLUGIN_ROOT}/scripts/gbsync.sh" update <bd_id>`
   - PULL on demand: `/gsd-beads:sync-pull`
   - Validate config without calling APIs: run a single
     `gbsync.sh update <bd_id>` and read the per-backend result lines.
