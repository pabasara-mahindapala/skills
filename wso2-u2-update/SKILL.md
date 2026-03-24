---
name: wso2-u2-update
description: "Apply WSO2 U2 updates to a WSO2 IS product distribution up to a defined update level. Handles online update (direct), offline update (create-update + apply-update), level pinning (--level), dry-run, revert, hotfix apply/revert, and current-state inspection. Keywords: wso2update, u2, update level, wso2is update, product update, security update, hotfix"
argument-hint: "Provide: WSO2_IS_HOME path, target update level (e.g. 7.1.0.50 or 'latest'), WSO2 credentials (username/password or env vars), online or offline mode"
---

# WSO2 U2 Update Skill

## When to Use
- Apply WSO2 IS updates to a specific update level (e.g., `wso2is-7.1.0.50`).
- Apply the latest available updates to a product distribution.
- Check current update level of a distribution.
- Preview (dry-run) what would change before applying.
- Create an offline update zip for air-gapped environments.
- Apply an offline update zip to a distribution.
- Apply or revert a WSO2 hotfix zip.
- Revert the last applied update batch.

## Required Inputs
1. `WSO2_IS_HOME` — absolute path to the product directory (e.g., `/opt/wso2is-7.1.0`)
   Must NOT be inside the backup directory (`~/.wso2-updates/backup/`).
2. `TARGET_LEVEL` — e.g., `7.1.0.50` (numeric suffix after product name), or `latest` to go to the latest level.
3. `WSO2_USERNAME` — WSO2 account email (e.g., `user@wso2.com`).
4. `WSO2_PASSWORD` — **NEVER ask the user for this.** Always retrieve silently from macOS Keychain:
   ```bash
   $(security find-internet-password -a '<USERNAME>' -w 2>/dev/null || security find-generic-password -a '<USERNAME>' -w 2>/dev/null)
   ```
   **NEVER print, echo, or display the retrieved password in any output.**
5. `PRODUCT_VERSION` — base product version, e.g., `5.10.0`, `5.11.0`, `7.1.0`, `7.2.0`.

## Update Tool Binary Location
The tool ships inside the product's `bin/` directory. Select the binary for the running OS:

| OS      | Binary                          |
|---------|---------------------------------|
| macOS   | `<WSO2_IS_HOME>/bin/wso2update_darwin`  |
| Linux   | `<WSO2_IS_HOME>/bin/wso2update_linux`   |
| Windows | `<WSO2_IS_HOME>/bin/wso2update_windows.exe` |

The tool auto-updates itself on first run if a newer version is available.
Update logs are written to: `<WSO2_IS_HOME>/updates/logs/wso2update-<date>.log`

## Update Level Format
- Full level identifier: `wso2is-<base-version>.<update-number>`
  Example: `wso2is-7.1.0.50`, `wso2is-5.10.0.390`
- When passing to `--level`, use only the last numeric segment: `--level 7.1.0.50`

## Commands Reference

### Password Macro
All commands that require `--password` must use this keychain lookup (replace `user@wso2.com` with the actual username):
```
--password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```
**Never ask the user for the password. Never display the retrieved value.**

### 1. Check Current State
Inspect the currently applied update level and any hotfixes:
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin current-state \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```

### 2. Check Available Updates (no changes applied)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin check \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```

### 3. Update to Latest Level (online)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```

### 4. Update to a Specific Level (online) — PRIMARY USE CASE
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level <PRODUCT_VERSION>.<UPDATE_NUMBER>
```
Example — pin wso2is-7.1.0 to update level 50:
```bash
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level 7.1.0.50
```

### 5. Dry-Run (simulate, no files modified)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level 7.1.0.50 \
  --dry-run
```

### 6. Update with Custom Backup Directory
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level 7.1.0.50 \
  --backup /path/to/backup/dir
```

### 7. Update Without Backup (not recommended for production)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level 7.1.0.50 \
  --no-backup
```

### 8. Revert Last Update
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin --revert
```

### 9. Verbose Mode (for troubleshooting)
Add `--verbose` to any command to see debug-level output:
```bash
./bin/wso2update_darwin \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --level 7.1.0.50 \
  --verbose
```

## Offline Update (Air-Gapped Environments)

### Step 1 — Create update zip (on an internet-connected machine)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin create-update \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --start-level <FROM_LEVEL> \
  --end-level <TO_LEVEL>
```
Example — create zip from level 7.1.0.40 to 7.1.0.50:
```bash
./bin/wso2update_darwin create-update \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)" \
  --start-level 7.1.0.40 \
  --end-level 7.1.0.50
```
Produces: `wso2is-7.1.0.40-7.1.0.50.zip`

### Step 2 — Apply update zip (on the air-gapped machine)
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin apply-update wso2is-7.1.0.40-7.1.0.50.zip
```
With revert option:
```bash
./bin/wso2update_darwin apply-update wso2is-7.1.0.40-7.1.0.50.zip --revert
```

## Hotfix Management

### Apply a hotfix zip
```bash
cd <WSO2_IS_HOME>
./bin/wso2update_darwin apply-hotfix wso2is-7.1.0-abc-hf1.zip \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```

### Apply hotfix offline (no credentials needed)
```bash
./bin/wso2update_darwin apply-hotfix wso2is-7.1.0-abc-hf1.zip --offline
```

### Revert most recent hotfix
```bash
./bin/wso2update_darwin revert-hotfix \
  --username user@wso2.com \
  --password "$(security find-internet-password -a 'user@wso2.com' -w 2>/dev/null || security find-generic-password -a 'user@wso2.com' -w 2>/dev/null)"
```

### Dry-run hotfix apply
```bash
./bin/wso2update_darwin apply-hotfix wso2is-7.1.0-abc-hf1.zip --dry-run
```

## Conflict Resolution
If the update reports merge conflicts:
1. Manually resolve the conflicting files in `<WSO2_IS_HOME>`.
2. Resume the update:
```bash
./bin/wso2update_darwin --continue
```

## Update Tool Version
```bash
./bin/wso2update_darwin version
```

## All Flags Summary

| Flag | Short | Description |
|------|-------|-------------|
| `--username` | `-u` | WSO2 account email |
| `--password` | `-p` | WSO2 account password |
| `--level` | `-l` | Target update level (e.g., `7.1.0.50`) |
| `--dry-run` | | Simulate update, no changes written |
| `--no-backup` | | Skip creating a product backup |
| `--backup` | `-b` | Custom backup directory path |
| `--revert` | | Revert to previous update level |
| `--continue` | | Resume after conflict resolution |
| `--channel` | `-c` | Update channel (default: `full`) |
| `--verbose` | `-v` | Enable verbose/debug output |
| `--template` | | Template for output format |

## Standard Workflow for Updating to a Defined Level

Follow these steps when given a `WSO2_IS_HOME` and a `TARGET_LEVEL`:

1. **Confirm the binary exists and is executable:**
   ```bash
   ls -la <WSO2_IS_HOME>/bin/wso2update_darwin
   chmod +x <WSO2_IS_HOME>/bin/wso2update_darwin
   ```

2. **Check the current state:**
   ```bash
   cd <WSO2_IS_HOME>
   ./bin/wso2update_darwin current-state \
     --username <USER> \
     --password "$(security find-internet-password -a '<USER>' -w 2>/dev/null || security find-generic-password -a '<USER>' -w 2>/dev/null)"
   ```

3. **Dry-run to preview changes:**
   ```bash
   ./bin/wso2update_darwin \
     --username <USER> \
     --password "$(security find-internet-password -a '<USER>' -w 2>/dev/null || security find-generic-password -a '<USER>' -w 2>/dev/null)" \
     --level <TARGET_LEVEL> --dry-run
   ```

4. **Apply the update:**
   ```bash
   ./bin/wso2update_darwin \
     --username <USER> \
     --password "$(security find-internet-password -a '<USER>' -w 2>/dev/null || security find-generic-password -a '<USER>' -w 2>/dev/null)" \
     --level <TARGET_LEVEL>
   ```

5. **Verify the new state:**
   ```bash
   ./bin/wso2update_darwin current-state \
     --username <USER> \
     --password "$(security find-internet-password -a '<USER>' -w 2>/dev/null || security find-generic-password -a '<USER>' -w 2>/dev/null)"
   ```

6. **If something goes wrong, revert:**
   ```bash
   ./bin/wso2update_darwin --revert
   ```

## Known Gotchas

- **Must run from `WSO2_IS_HOME`** — running from inside `~/.wso2-updates/backup/` will error.
- **Backup directory** defaults to `~/.wso2-updates/backup/wso2is-<version>-<uuid>/` — ensure disk space is available.
- **The tool self-updates** on first authenticated run — the binary version may change before the actual product update runs; this is normal.
- **Token caching** — credentials are cached in `<WSO2_IS_HOME>/updates/config.json` after first successful auth.
- **`--level` takes the full dotted version** including the base version: e.g., `7.1.0.50` not just `50`.
- **`--end-level 0`** in `create-update` means latest (the default).

## Output Expectations

When invoked, produce:
1. The exact command(s) to run for the given inputs.
2. The expected output lines to confirm success (level name, update count).
3. The revert command in case rollback is needed.
4. Any pre/post steps specific to the product version (e.g., H2 DB backup for local dev).
