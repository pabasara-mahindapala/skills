# Skills

AI agent skill files that I use locally in my setup.

Each skill folder contains a `SKILL.md` file with details on the skill.

## Skills

| Skill | Description |
|-------|-------------|
| [wso2-is](./wso2-is/) | WSO2 Identity Server — configs, deployment paths, logs, webapps, bundles |
| [wso2-u2-update](./wso2-u2-update/) | WSO2 U2 update tool — online/offline updates, level pinning, hotfix apply/revert |
| [wso2-security-scan](./wso2-security-scan/) | WSO2 Product Security Vulnerability Scan — analyze SCA reports, locate vulnerable components, assess exploitability |
| [wso2-is-docs](./wso2-is-docs/) | WSO2 Identity Server documentation search from a local clone of the docs repo |
| [wso2-is-troubleshoot](./wso2-is-troubleshoot/) | WSO2 IS authorization code flow troubleshooting — audit log correlation, adaptive auth tracing, HAR/access log analysis |

## Usage

Skills are consumed by AI agents via:
- **GitHub Copilot**: `~/.copilot/skills/`
- **Claude**: `~/.claude/skills/`

Use the sync script to keep local skill directories in sync with this repo.
