---
name: delete-claude-session
description: >
  Permanently delete every on-disk record of one specific Claude Code session -- transcript,
  per-session directory, session-env, plugin transcript caches, history.jsonl entries and
  lastSessionId config pointers -- without affecting any other session. Always shows a full
  inventory and requires explicit user confirmation before deleting, and creates no backups.
  Use when the user wants to remove, purge, erase, wipe or scrub a Claude Code session, chat
  or conversation from disk. Keywords: delete session, remove session, purge session, erase
  chat history, wipe conversation, scrub transcript, forget this session, clear session
  records, delete claude history, remove jsonl transcript.
---

# Delete One Claude Code Session

Removes a single session's records completely and leaves every other session intact.
**Irreversible, and no backups are kept** -- so confirmation is mandatory.

## Where a session's records live

A session is not one file. Its records are scattered across seven places:

| Location | Scope | Handling |
|---|---|---|
| `~/.claude/projects/<proj>/<sid>.jsonl` | this session only | delete |
| `~/.claude/projects/<proj>/<sid>/` (custom-title, tool-results) | this session only | delete |
| `~/.claude/session-env/<sid>/` | this session only | delete |
| `~/.claude/plugins/*/transcript-cache/<hash>.json` | this session only | delete (matched by content -- the filename is a hash that changes) |
| `~/.claude/history.jsonl` | **shared** | strip only entries whose own `sessionId` matches |
| `~/.claude.json` → `projects[*].lastSessionId` | **shared** | remove the key only when it points at this session |
| `~/.claude/backups/.claude.json.backup.*` | **shared** | same, in each existing backup |

Anything marked *shared* is edited in place via atomic replace, never deleted wholesale.
That distinction is what keeps other sessions safe -- do not shortcut it with `rm` or a
blanket `grep -v`.

## Procedure

**1. Identify the session.** If the user gave a UUID, use it. Otherwise list candidates:

```bash
scripts/scan.py --list                 # 20 most recent, newest first
scripts/scan.py --list my-project      # filter by project path substring
```

Each row shows the id, project, timestamp and title or first prompt. If more than one
plausibly matches what the user described, ask which one -- never guess. The running
session is tagged `[LIVE]`.

**2. Scan.** This is read-only and deletes nothing:

```bash
scripts/scan.py <session-id>
```

It prints the session's identity (project, title, first prompt, size) and three lists:
what gets deleted outright, what gets stripped in place, and what will *not* be touched.

**3. Confirm — mandatory, never skip.** Show the user the scan output, including which
session it is by title and first prompt, so they can tell it is the right one. Then ask
for explicit confirmation with `AskUserQuestion`, making clear it is permanent and that
no backup will exist. Proceed only on an unambiguous yes. If the user's instruction was
already an explicit delete request naming that session, still confirm once: the scan may
reveal the session is larger, or is a different one, than they assumed.

**4. Purge.**

```bash
scripts/purge.py <session-id> --confirm
```

It refuses without `--confirm`, re-scans afterwards and reports whether anything remains.

## The live-session case

If the target is the session you are running in, `scan.py` flags it and `purge.py` refuses
(override: `--allow-live`). Deleting it mid-session does not stick -- the harness holds the
transcript open and rewrites it on exit. Tell the user to quit Claude Code first, then hand
them the command to run themselves. Their shell history will then hold the session id;
mention prefixing the command with a space if `HIST_IGNORE_SPACE` is set in their shell.

## Sessions that mention other sessions

If session B's transcript quotes session A's id (because the user discussed A inside B),
the scan reports it under *will not touch*. That text belongs to B's record, not A's.
Removing it means deleting from B -- a separate decision. Surface it and let the user choose
rather than folding it into the purge.

## Rules

- Never delete without showing the scan output and getting an explicit yes.
- Never create a backup copy -- the point is that the records are gone.
- Never touch a path the scan did not list.
- Scope every edit to shared files by `sessionId` equality, not by substring match.
- Report honestly: if `purge.py` exits nonzero, say what survived instead of claiming success.
