#!/usr/bin/env python3
"""Permanently delete every on-disk record of ONE Claude Code session.

  purge.py <session-id> --confirm [--allow-live]

Refuses to run without --confirm. Creates no backups; the deletion is
irreversible. Only ever touches records whose own sessionId is the target --
other sessions' files are left alone.
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_records as R


def strip_history(sid):
    p = os.path.join(R.CLAUDE, "history.jsonl")
    if not os.path.exists(p):
        return 0
    keep, removed = [], 0
    for line in open(p, errors="replace"):
        try:
            hit = json.loads(line).get("sessionId") == sid
        except Exception:
            hit = False          # unparseable lines are preserved as-is
        if hit:
            removed += 1
        else:
            keep.append(line)
    if removed:
        tmp = p + ".tmp"
        with open(tmp, "w") as fh:
            fh.writelines(keep)
        os.replace(tmp, p)
    return removed


def strip_config(entry, sid):
    p = entry["path"]
    try:
        d = json.load(open(p))
    except Exception:
        return 0
    n = 0
    for proj in (d.get("projects") or {}).values():
        if isinstance(proj, dict) and proj.get("lastSessionId") == sid:
            del proj["lastSessionId"]
            n += 1
    if n:
        tmp = p + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(d, fh, indent=2)
        os.replace(tmp, p)
    return n


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    sid = argv[0]
    flags = set(argv[1:])

    if not R.valid(sid):
        print(f"ERROR: '{sid}' is not a session UUID.", file=sys.stderr)
        return 2
    if "--confirm" not in flags:
        print("ERROR: refusing to delete without --confirm.", file=sys.stderr)
        print(f"Review first:  scan.py {sid}", file=sys.stderr)
        return 2
    if R.is_probably_live(sid) and "--allow-live" not in flags:
        print("ERROR: this looks like the RUNNING session (transcript modified <2 min ago).",
              file=sys.stderr)
        print("Deleting it now will not stick -- the harness rewrites it on exit.", file=sys.stderr)
        print("Quit Claude Code and rerun, or pass --allow-live to override.", file=sys.stderr)
        return 3

    plan = R.collect(sid)
    if not (plan["delete"] or plan["strip_history"] or plan["config"]):
        print(f"No records found for {sid}. Nothing done.")
        return 1

    for p in plan["delete"]:
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            print(f"deleted  {p}")
        except OSError as e:
            print(f"FAILED   {p}: {e}", file=sys.stderr)

    n = strip_history(sid)
    if n:
        print(f"stripped {n} entr{'y' if n == 1 else 'ies'} from history.jsonl")
    for entry in plan["config"]:
        if strip_config(entry, sid):
            print(f"stripped lastSessionId from {os.path.basename(entry['path'])}")

    # Verify: re-scan for anything the target still owns.
    left = R.collect(sid)
    owned = len(left["delete"]) + left["strip_history"] + len(left["config"])
    print()
    if owned:
        print(f"WARNING: {owned} record(s) still present. Re-run scan.py to inspect.")
        return 4
    print(f"Clean -- no records of {sid} remain.")
    if left["foreign"]:
        print(f"\n{len(left['foreign'])} other session transcript(s) still mention this id "
              "(left untouched by design):")
        for f in left["foreign"]:
            print(f"  {f}")
    print("\nNote: your shell history may retain the session id if you ran this by hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
