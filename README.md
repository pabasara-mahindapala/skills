# Skills

AI agent skill files that I use locally in my setup.

Each skill folder contains a `SKILL.md` file with details on the skill.

## Skills

| Skill | Description |
|-------|-------------|
| [azure-log-csv-to-plain](./azure-log-csv-to-plain/) | Convert Azure-exported log CSV files into readable plain log files with reformatted inline JSON |
| [export-html-report](./export-html-report/) | Generate a self-contained, presentation-ready HTML report from completed analysis or conversation output |
| [wso2-u2-update](./wso2-u2-update/) | WSO2 U2 update tool — online/offline updates, level pinning, hotfix apply/revert |
| [wso2-security-scan](./wso2-security-scan/) | WSO2 Product Security Vulnerability Scan — analyze SCA reports, locate vulnerable components, assess exploitability |
| [wso2-is-docs](./wso2-is-docs/) | WSO2 Identity Server documentation search from a local clone of the docs repo |
| [wso2-is-troubleshoot](./wso2-is-troubleshoot/) | WSO2 IS authorization code flow troubleshooting — audit log correlation, adaptive auth tracing, HAR/access log analysis |
| [wso2-local-smtp-sink](./wso2-local-smtp-sink/) | Local SMTP sink for a local WSO2 IS — capture every outbound email as an `.eml` file to read links and codes |
| [delete-claude-session](./delete-claude-session/) | Permanently delete all on-disk records of one Claude Code session, with inventory and explicit confirmation |
| [checkpointed-execution](./checkpointed-execution/) | Work one step at a time, stopping for review or confirmation between steps |
| [set-display](./set-display/) | Set an external display's resolution and refresh rate on macOS, including modes System Settings hides |
| [local-autocomplete-continue-ollama](./local-autocomplete-continue-ollama/) | Maintain local VS Code tab autocomplete with Continue + Ollama (Qwen2.5-Coder) — switch models, tune, troubleshoot |
| [caveman](./caveman/) | Skill that makes agent talk like caveman from [juliusbrussee](https://github.com/juliusbrussee/caveman) |

## Usage

Skills are consumed by AI agents via:
- **GitHub Copilot and many more**: `~/.agents/skills/`
- **Claude**: `~/.claude/skills/`

Use the sync script to keep local skill directories in sync with this repo.
