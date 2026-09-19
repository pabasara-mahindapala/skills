#!/usr/bin/env python3
"""Read-only inventory of everything on disk for one Claude Code session.

  scan.py --list [project-substring]   list recent sessions to pick from
  scan.py <session-id>                 show the full deletion plan

Deletes nothing. Run this first and show the user the output.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_records as R


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def do_list(args):
    rows = R.recent(limit=20, project_filter=args[0] if args else None)
    if not rows:
        print("No sessions found.")
        return 0
    print(f"{'MODIFIED':<17} {'SESSION ID':<38} PROJECT / TITLE")
    for r in rows:
        tag = "  [LIVE]" if r["live"] else ""
        print(f"{r['modified']:<17} {r['sid']:<38} {r['project']}{tag}")
        label = r["title"] or (r["prompt"] or "")[:90].replace("\n", " ")
        if label:
            print(f"{'':<17} {'':<38}   ↳ {label}")
    return 0


def do_scan(sid):
    if not R.valid(sid):
        print(f"ERROR: '{sid}' is not a session UUID.", file=sys.stderr)
        return 2

    meta = R.describe(sid)
    plan = R.collect(sid)
    total = len(plan["delete"]) + plan["strip_history"] + len(plan["config"])
    if total == 0:
        print(f"No records found for {sid}. Nothing to delete.")
        return 1

    print(f"SESSION {sid}")
    if meta:
        print(f"  project     : {meta['project']}")
        print(f"  title       : {meta['title'] or '(none)'}")
        print(f"  started     : {meta['started'] or '?'}")
        print(f"  last modified: {meta['modified']}")
        print(f"  transcript  : {human(meta['size'])}")
        if meta["first_prompt"]:
            p = meta["first_prompt"].replace("\n", " ")
            print(f"  first prompt: {p[:160]}{'...' if len(p) > 160 else ''}")
    else:
        print("  (no transcript; only residual references remain)")

    if R.is_probably_live(sid):
        print("\n  !! WARNING: this transcript was modified in the last 2 minutes.")
        print("     It is almost certainly the RUNNING session. Deleting it now will not")
        print("     stick -- the harness rewrites the file on exit. Quit Claude Code first.")

    print("\nWILL DELETE ENTIRELY (belongs to this session alone):")
    if plan["delete"]:
        for p in plan["delete"]:
            kind = "dir " if os.path.isdir(p) else "file"
            size = ""
            if os.path.isfile(p):
                size = f"  ({human(os.path.getsize(p))})"
            print(f"  [{kind}] {p}{size}")
    else:
        print("  (nothing)")

    print("\nWILL STRIP IN PLACE (shared files -- only this session's entries):")
    if plan["strip_history"]:
        print(f"  history.jsonl            {plan['strip_history']} prompt entr"
              f"{'y' if plan['strip_history'] == 1 else 'ies'}")
    for c in plan["config"]:
        print(f"  {os.path.basename(c['path']):<24} lastSessionId for: {', '.join(c['projects'])}")
    if not plan["strip_history"] and not plan["config"]:
        print("  (nothing)")

    print("\nWILL NOT TOUCH (other sessions that merely mention this id):")
    if plan["foreign"]:
        for f in plan["foreign"]:
            print(f"  {f}")
        print("  ^ these belong to OTHER sessions. Removing them is a separate decision.")
    else:
        print("  (nothing)")

    print("\nNo backups are created. Every write is an atomic in-place replace.")
    print(f"To proceed:  purge.py {sid} --confirm")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] in ("--list", "-l"):
        return do_list(argv[1:])
    return do_scan(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
