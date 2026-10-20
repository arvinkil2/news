#!/usr/bin/env python3
"""Atomic GitHub publisher for the news site.

Publishes a set of local files to arvinkil2/news in ONE commit via the
GitHub git-database API (no local git, no SSH, no browser).

Usage:
  publish.py --message "msg" local_path:repo/path [local_path:repo/path ...]

Locking: takes an exclusive flock on /tmp/news-publish.lock so overlapping
cron jobs serialize instead of clobbering each other.

Exit 0 on success (prints commit sha + URL). Exit 1 on failure.
"""
import base64
import fcntl
import hashlib
import http.client
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, ensure_allowed_url

API = "https://api.github.com"
CRED = os.environ.get("GITHUB_CRED", "custom.github-pat")
ALLOWED = ["api.github.com"]
OWNER, REPO, BRANCH = "arvinkil2", "news", "main"
LOCKFILE = "/tmp/news-publish.lock"


def req(method, path, data=None):
    url = API + path
    ensure_allowed_url(url, ALLOWED)
    body = json.dumps(data).encode() if data is not None else None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "muse-news-publish",
    }
    if body:
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    add_surrogate_to_request(r, CRED, allowed_hosts=ALLOWED)
    try:
        resp = urllib.request.urlopen(r, timeout=60)
    except (http.client.RemoteDisconnected, http.client.BadStatusLine,
            socket.timeout, ConnectionResetError,
            urllib.error.URLError, ssl.SSLError) as e:
        # Transient connection drop: retry up to 4 times with backoff.
        # Blob POSTs are idempotent, so this is safe. URLError/SSLError
        # added 2026-10-15: the evening's publish failures were SSL EOF
        # errors ("EOF occurred in violation of protocol"), which arrive
        # wrapped in URLError and previously bypassed this retry block.
        for attempt in range(4):
            time.sleep(2 * (attempt + 1))
            try:
                resp = urllib.request.urlopen(r, timeout=60)
                break
            except (http.client.RemoteDisconnected, http.client.BadStatusLine,
                    socket.timeout, ConnectionResetError,
                    urllib.error.URLError, ssl.SSLError):
                if attempt == 3:
                    raise RuntimeError(
                        f"Connection dropped 5 times on {method} {path}: giving up")
                continue
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:2000]
        raise RuntimeError(f"HTTP {e.code} {e.reason} on {method} {path}: {detail}")
    raw = resp.read()
    return json.loads(raw) if raw else {}


def blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode()
                        + b"\x00" + content).hexdigest()


def publish(pairs, message):
    # 1. current head
    ref = req("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
    head_sha = ref["object"]["sha"]
    head_commit = req("GET", f"/repos/{OWNER}/{REPO}/git/commits/{head_sha}")

    # 1b. existing blob shas, to skip files whose content is unchanged
    existing = {}
    try:
        full = req("GET", f"/repos/{OWNER}/{REPO}/git/trees/"
                          f"{head_commit['tree']['sha']}?recursive=1")
        if not full.get("truncated"):
            existing = {e["path"]: e["sha"] for e in full.get("tree", [])
                        if e.get("type") == "blob"}
    except RuntimeError:
        existing = {}

    # 2. build tree entries (blobs first); unchanged files are skipped
    pending = []   # (repo_path, content) needing a blob upload
    tree = []
    skipped = 0
    for local, repo_path in pairs:
        if local == "DELETE":
            # Null-sha tree entry on top of base_tree deletes the path.
            tree.append({"path": repo_path, "mode": "100644",
                         "type": "blob", "sha": None})
            continue
        with open(local, "rb") as f:
            content = f.read()
        if existing.get(repo_path) == blob_sha(content):
            skipped += 1
            continue
        pending.append((repo_path, content))

    def upload(item):
        repo_path, content = item
        blob = req("POST", f"/repos/{OWNER}/{REPO}/git/blobs", {
            "content": base64.b64encode(content).decode(),
            "encoding": "base64",
        })
        return {"path": repo_path, "mode": "100644",
                "type": "blob", "sha": blob["sha"]}

    if pending:
        # A blob whose connection drops repeatedly must not abort the
        # whole publish (2026-10-15: evening egress flakiness killed
        # entire chunks this way; one failed upload discarded hundreds
        # of good ones). Failed uploads get one serial retry pass,
        # spaced out, before the publish gives up.
        def upload_safe(item):
            try:
                return upload(item)
            except Exception:
                return None
        with ThreadPoolExecutor(max_workers=6) as ex:
            done = list(ex.map(upload_safe, pending))
        failed = [it for it, r in zip(pending, done) if r is None]
        tree.extend(r for r in done if r is not None)
        for item in failed:
            time.sleep(3)
            tree.append(upload(item))
    if skipped:
        print(f"publish: skipped {skipped} unchanged of {len(pairs)}",
              file=sys.stderr)
    if not tree:
        return head_sha  # nothing changed; no commit needed

    # 3. new tree on top of head's tree
    new_tree = req("POST", f"/repos/{OWNER}/{REPO}/git/trees", {
        "base_tree": head_commit["tree"]["sha"],
        "tree": tree,
    })

    # 4. commit
    new_commit = req("POST", f"/repos/{OWNER}/{REPO}/git/commits", {
        "message": message,
        "tree": new_tree["sha"],
        "parents": [head_sha],
    })

    # 5. move branch (fast-forward only: if head moved, retry once)
    try:
        req("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", {
            "sha": new_commit["sha"],
        })
    except RuntimeError as e:
        if "422" in str(e):
            return publish(pairs, message)  # head moved; rebuild on new head
        raise
    return new_commit["sha"]


def main():
    args = sys.argv[1:]
    if "--message" not in args:
        print("usage: publish.py --message MSG local:repo/path ...", file=sys.stderr)
        sys.exit(2)
    mi = args.index("--message")
    message = args[mi + 1]
    pairs = []
    for spec in args[mi + 2:]:
        local, repo_path = spec.split(":", 1)
        if local != "DELETE" and not os.path.isfile(local):
            print(f"missing local file: {local}", file=sys.stderr)
            sys.exit(2)
        pairs.append((local, repo_path))
    if not pairs:
        print("nothing to publish", file=sys.stderr)
        sys.exit(2)

    with open(LOCKFILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            sha = publish(pairs, message)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)

    url = f"https://github.com/{OWNER}/{REPO}/commit/{sha}"
    print(json.dumps({"commit": sha, "url": url}))


if __name__ == "__main__":
    main()
