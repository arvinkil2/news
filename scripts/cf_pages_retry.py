#!/usr/bin/env python3
"""Retry the latest Cloudflare Pages production deployment for kilambi-news.

Replaces the fragile browser-dashboard "Retry deployment" step (Cloudflare's
human-verification challenge blocks our datacenter IP). Uses a Cloudflare API
token with Account -> Cloudflare Pages: Edit, stored in the Secure Vault as
connector custom.cloudflare (Bearer header placement).

Usage:
  python3 cf_pages_retry.py            # retry latest production deployment if it failed
  python3 cf_pages_retry.py --check    # just report latest deployment status
  python3 cf_pages_retry.py --force    # retry latest regardless of status

Exit 0 on success (or when nothing needed retrying). Exit 1 on API failure.
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, ensure_allowed_url

API = "https://api.cloudflare.com/client/v4"
CRED = os.environ.get("CLOUDFLARE_CRED", "custom.cloudflare")
ALLOWED = ["api.cloudflare.com"]
PROJECT = "kilambi-news"
# Account ID cannot be discovered via GET /accounts with a Pages-scoped token
# (the token cannot list accounts), so it is stored in a local config file.
ACCOUNT_ID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "cf_account_id.txt")


def req(method, path, data=None):
    url = API + path
    ensure_allowed_url(url, ALLOWED)
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"}
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    add_surrogate_to_request(r, CRED, allowed_hosts=ALLOWED)
    try:
        resp = urllib.request.urlopen(r, timeout=60)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:1000]
        raise RuntimeError(f"HTTP {e.code} on {method} {path}: {detail}")
    raw = resp.read()
    out = json.loads(raw) if raw else {}
    if not out.get("success", True):
        raise RuntimeError(f"API error on {method} {path}: {out.get('errors')}")
    return out.get("result")


def find_account_with_project():
    # Preferred: account ID from local config file (Pages-scoped tokens
    # cannot list accounts via GET /accounts).
    try:
        with open(ACCOUNT_ID_FILE) as f:
            aid = f.read().strip()
        if aid:
            info = req("GET", f"/accounts/{aid}/pages/projects/{PROJECT}")
            return aid, info.get("name", aid)
    except (OSError, RuntimeError):
        pass
    # Fallback: discover via account listing (needs broader token perms).
    accounts = req("GET", "/accounts")
    if not accounts:
        raise RuntimeError("token has access to no accounts")
    for acct in accounts:
        aid = acct["id"]
        try:
            req("GET", f"/accounts/{aid}/pages/projects/{PROJECT}")
            return aid, acct.get("name", aid)
        except RuntimeError:
            continue
    raise RuntimeError(f"project {PROJECT} not found in any accessible account")


def latest_production_deployment(account_id):
    deps = req(
        "GET",
        f"/accounts/{account_id}/pages/projects/{PROJECT}/deployments"
        "?env=production&per_page=5",
    )
    if not deps:
        raise RuntimeError("no production deployments found")
    return deps[0]


def main():
    check_only = "--check" in sys.argv
    force = "--force" in sys.argv
    try:
        account_id, account_name = find_account_with_project()
        dep = latest_production_deployment(account_id)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    dep_id = dep["id"]
    short = dep.get("short_id", dep_id[:8])
    stage = (dep.get("latest_stage") or {}).get("status", "unknown")
    build = (dep.get("latest_stage") or {}).get("name", "")
    commit = ((dep.get("deployment_trigger") or {}).get("metadata") or {}).get(
        "commit_hash", ""
    )[:8]
    print(f"account: {account_name}")
    print(f"latest production deployment: {short} (commit {commit})")
    print(f"latest stage: {build} -> {stage}")

    needs_retry = force or stage in ("failure", "failed")
    if check_only or not needs_retry:
        print("no retry needed" if not check_only else "check complete")
        return 0

    print(f"retrying deployment {short} ...")
    try:
        result = req(
            "POST",
            f"/accounts/{account_id}/pages/projects/{PROJECT}"
            f"/deployments/{dep_id}/retry",
            data={},
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    new_id = (result or {}).get("id", "?")[:8]
    print(f"retry accepted, new deployment id: {new_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
