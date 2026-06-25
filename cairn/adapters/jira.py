#!/usr/bin/env python3
"""Jira Cloud adapter for cairn (REST v3, stdlib only).

config (sync.json):
{
  "base_url": "https://yourorg.atlassian.net",   # required
  "project_key": "CHN",                          # required
  "issue_type": "Task",                          # optional (default Task)
  "email_env": "JIRA_EMAIL",                     # env var holding the account email
  "token_env": "JIRA_API_TOKEN",                 # env var holding the API token
  "transitions": { "in_progress": "In Progress", "closed": "Done" }
}

Auth: HTTP Basic with <email>:<api_token> (Atlassian Cloud). Create a token at
https://id.atlassian.com/manage-profile/security/api-tokens and export both env
vars before syncing. Status normalization on pull uses Jira's statusCategory
(new->open, indeterminate->in_progress, done->closed), which is robust across
workflow configs.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

CAT = {"new": "open", "indeterminate": "in_progress", "done": "closed"}


def cfg_auth(cfg):
    email = os.environ.get(cfg.get("email_env", "JIRA_EMAIL"), "")
    token = os.environ.get(cfg.get("token_env", "JIRA_API_TOKEN"), "")
    if not email or not token:
        print("jira adapter: missing email/token env vars "
              f"({cfg.get('email_env','JIRA_EMAIL')} / {cfg.get('token_env','JIRA_API_TOKEN')})",
              file=sys.stderr)
        sys.exit(1)
    return "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()


def api(cfg, method, path, body=None):
    url = cfg["base_url"].rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", cfg_auth(cfg))
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"jira {method} {path} -> {e.code}: {e.read().decode()[:300]}",
              file=sys.stderr)
        sys.exit(1)


def adf(text):
    return {"type": "doc", "version": 1,
            "content": [{"type": "paragraph",
                         "content": [{"type": "text", "text": text or " "}]}]}


def adf_to_text(node):
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    return "".join(adf_to_text(c) for c in node.get("content", []))


def transition(cfg, key, target_name):
    if not target_name:
        return
    ts = api(cfg, "GET", f"/rest/api/3/issue/{key}/transitions").get("transitions", [])
    for t in ts:
        if t.get("to", {}).get("name", "").lower() == target_name.lower() \
                or t.get("name", "").lower() == target_name.lower():
            api(cfg, "POST", f"/rest/api/3/issue/{key}/transitions",
                {"transition": {"id": t["id"]}})
            return


def push(event, cfg):
    ext = event.get("external_id")
    action = event["action"]
    trans = cfg.get("transitions", {})
    if action == "create" or (action == "update" and not ext):
        body = {"fields": {
            "project": {"key": cfg["project_key"]},
            "summary": event["title"],
            "description": adf(event["body"]),
            "issuetype": {"name": cfg.get("issue_type", "Task")},
        }}
        key = api(cfg, "POST", "/rest/api/3/issue", body).get("key", "")
        if event["status"] == "in_progress":
            transition(cfg, key, trans.get("in_progress"))
        return key
    if action == "update":
        api(cfg, "PUT", f"/rest/api/3/issue/{ext}",
            {"fields": {"summary": event["title"], "description": adf(event["body"])}})
        if event["status"] == "in_progress":
            transition(cfg, ext, trans.get("in_progress"))
        elif event["status"] == "closed":
            transition(cfg, ext, trans.get("closed"))
        return ext
    if action == "close":
        if ext:
            transition(cfg, ext, trans.get("closed", "Done"))
        return ext or ""
    print(f"unknown action {action}", file=sys.stderr)
    sys.exit(1)


def pull(cfg, items):
    out = []
    for it in items:
        ext = it.get("external_id")
        if not ext:
            continue
        try:
            d = api(cfg, "GET",
                    f"/rest/api/3/issue/{ext}?fields=summary,description,status,updated")
        except SystemExit:
            continue
        f = d.get("fields", {})
        cat = f.get("status", {}).get("statusCategory", {}).get("key", "new")
        out.append({
            "bd_id": it["bd_id"], "external_id": d.get("key", ext),
            "title": f.get("summary", ""),
            "body": adf_to_text(f.get("description")) if f.get("description") else "",
            "status": CAT.get(cat, "open"),
            "updated_at": f.get("updated"),
        })
    return out


def main():
    event = json.load(sys.stdin)
    cfg = event.get("config", {})
    for req in ("base_url", "project_key"):
        if req not in cfg:
            print(f"jira adapter: config.{req} is required", file=sys.stderr)
            sys.exit(1)
    if event["action"] == "pull":
        print(json.dumps(pull(cfg, event.get("items", []))))
    else:
        print(push(event, cfg))


if __name__ == "__main__":
    main()
