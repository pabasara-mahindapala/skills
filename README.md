# Skills

AI agent skill files for GitHub Copilot and Claude.

Each skill folder contains a `SKILL.md` with domain-specific instructions and best practices.

## Skills

| Skill | Description |
|-------|-------------|
| [wso2-is](./wso2-is/) | WSO2 Identity Server (5.11.x) — configs, deployment paths, logs, webapps, bundles |
| [wso2-u2-update](./wso2-u2-update/) | WSO2 U2 update tool — online/offline updates, level pinning, hotfix apply/revert |

## Usage

Skills are consumed by AI agents via:
- **GitHub Copilot**: `~/.copilot/skills/`
- **Claude**: `~/.claude/skills/`

Use the sync script to keep local skill directories in sync with this repo.
