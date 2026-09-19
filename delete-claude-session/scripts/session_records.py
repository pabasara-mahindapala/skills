#!/usr/bin/env python3
"""Locate every on-disk record belonging to a single Claude Code session.

Read-only. Shared by scan.py and purge.py so both agree on what "all records"
means. Nothing here deletes anything.
"""
import json
import os
import re
import time
from glob import glob

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
CONFIG = os.path.join(HOME, ".claude.json")
PROJECTS = os.path.join(CLAUDE, "projects")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)

# Files that legitimately hold references to MANY sessions. These are never
# deleted wholesale -- only the target session's own entries are stripped.
SHARED_FILES = {"history.jsonl"}


def valid(sid):
    return bool(UUID_RE.match(sid or ""))


def transcript_path(sid):
    for p in glob(os.path.join(PROJECTS, "*", sid + ".jsonl")):
        return p
    return None


def _first_prompt(path):
    """Return (title, first user prompt, project dir, timestamp) from a transcript."""
    title = prompt = project = ts = None
    try:
        with open(path, errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 400:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("customTitle") and not title:
                    title = d["customTitle"]
                elif d.get("aiTitle") and not title:
                    title = d["aiTitle"]
                if not prompt and d.get("type") == "user" and not d.get("isMeta"):
                    c = (d.get("message") or {}).get("content")
                    if isinstance(c, list):
                        c = " ".join(x.get("text", "") for x in c
                                     if isinstance(x, dict) and x.get("type") == "text")
                    c = (c or "").strip()
                    if c and not c.startswith("<"):
                        prompt = c
                        ts = d.get("timestamp")
                a = d.get("attachment") or {}
                if not project and a.get("type") == "environment":
                    project = (a.get("snapshot") or {}).get("workingDirectory")
    except OSError:
        pass
    return title, prompt, project, ts


def describe(sid):
    """Human-facing metadata about the session, or {} if there is no transcript."""
    p = transcript_path(sid)
    if not p:
        return {}
    title, prompt, project, ts = _first_prompt(p)
    st = os.stat(p)
    return {
        "transcript": p,
        "title": title,
        "first_prompt": prompt,
        "project": project or os.path.basename(os.path.dirname(p)),
        "started": ts,
        "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
        "age_seconds": time.time() - st.st_mtime,
        "size": st.st_size,
    }


def is_probably_live(sid):
    """A transcript touched in the last 2 minutes is very likely the running session."""
    d = describe(sid)
    return bool(d) and d["age_seconds"] < 120


def collect(sid):
    """Return the deletion plan for `sid`.

    delete        -- paths removed entirely (belong to this session alone)
    strip_history -- history.jsonl entry count to remove
    config        -- config files holding a lastSessionId pointing at this session
    foreign       -- OTHER sessions' transcripts that merely mention the id; never touched
    """
    plan = {"delete": [], "strip_history": 0, "config": [], "foreign": []}

    # 1. Anything named after the session: transcript, per-session dir, session-env.
    for pat in (os.path.join(PROJECTS, "*", sid + ".jsonl"),
                os.path.join(PROJECTS, "*", sid),
                os.path.join(CLAUDE, "session-env", sid)):
        plan["delete"].extend(sorted(glob(pat)))

    # 2. Plugin caches keyed by transcript content (claude-hud and friends).
    #    Matched by content because the cache filename is a hash that changes.
    for cache_dir in glob(os.path.join(CLAUDE, "plugins", "*", "transcript-cache")):
        for f in sorted(glob(os.path.join(cache_dir, "*.json"))):
            try:
                if sid in open(f, errors="replace").read():
                    plan["delete"].append(f)
            except OSError:
                pass

    # 3. history.jsonl -- count only entries whose OWN sessionId is the target.
    hist = os.path.join(CLAUDE, "history.jsonl")
    if os.path.exists(hist):
        n = 0
        for line in open(hist, errors="replace"):
            try:
                if json.loads(line).get("sessionId") == sid:
                    n += 1
            except Exception:
                pass
        plan["strip_history"] = n

    # 4. lastSessionId pointers in the live config and its existing backups.
    for p in [CONFIG] + sorted(glob(os.path.join(CLAUDE, "backups", ".claude.json.backup.*"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        hits = [k for k, v in (d.get("projects") or {}).items()
                if isinstance(v, dict) and v.get("lastSessionId") == sid]
        if hits:
            plan["config"].append({"path": p, "projects": hits})

    # 5. Other sessions' transcripts that merely mention the id (e.g. a session
    #    where you discussed this one). Reported, never modified.
    already = set(plan["delete"])
    for f in glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        if f in already or os.path.basename(f) == sid + ".jsonl":
            continue
        try:
            if sid in open(f, errors="replace").read():
                plan["foreign"].append(f)
        except OSError:
            pass
    plan["foreign"].sort()
    return plan


def recent(limit=15, project_filter=None):
    """List recent sessions as (mtime, sid, project, title, prompt)."""
    out = []
    for f in glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        sid = os.path.basename(f)[:-6]
        if not valid(sid):
            continue
        proj = os.path.basename(os.path.dirname(f))
        if project_filter and project_filter.lower() not in proj.lower():
            continue
        out.append((os.stat(f).st_mtime, sid, proj, f))
    out.sort(reverse=True)
    rows = []
    for mt, sid, proj, f in out[:limit]:
        title, prompt, _, _ = _first_prompt(f)
        rows.append({
            "sid": sid, "project": proj, "title": title, "prompt": prompt,
            "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(mt)),
            "live": (time.time() - mt) < 120,
        })
    return rows
