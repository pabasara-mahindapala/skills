---
name: local-autocomplete-continue-ollama
description: Maintain the local tab-autocomplete setup in VS Code - the Continue extension backed by Ollama running a Qwen2.5-Coder base model on this Mac. Use to switch or try a different model (e.g. Qwen2.5-Coder 7B), change keep-alive or other Continue options, check status and memory, troubleshoot missing suggestions, or remove the setup. 
Keywords: continue, ollama, tab autocomplete, ghost text, qwen2.5-coder, local model, config.yaml, keepAlive, fim.
---

# Local tab autocomplete: Continue + Ollama

VS Code shows grey inline suggestions (Tab to accept) from a model running on this Mac. Nothing leaves the machine. Set up to replace Supermaven (sunset) and capped Copilot free plan.

```
VS Code ── Continue extension ──HTTP──> Ollama (127.0.0.1:11434) ──> qwen2.5-coder:1.5b-base (GPU)
```

## Current setup

| Piece | Where / value |
|---|---|
| Ollama | Homebrew formula, service `sh.brew.ollama` (starts at login), listens on `127.0.0.1:11434` only |
| Ollama log | `/opt/homebrew/var/log/ollama.log` (one `POST "/api/generate"` line per suggestion) |
| Models on disk | `~/.ollama/models/` |
| Model in use | `qwen2.5-coder:1.5b-base` (986 MB, ~1.3 GB loaded at 8K context, 100% GPU) |
| Continue config | `~/.continue/config.yaml` (Continue reloads it on save, no window reload needed) |
| VS Code settings | `~/Library/Application Support/Code/User/settings.json`: `"continue.telemetryEnabled": false`, `github.copilot.enable` all `false` (stops Copilot fighting over Tab). Next Edit left at default (on). |
| Setup runbook | `~/checkpoints/continue-ollama/runbook.md` |

Current `~/.continue/config.yaml`:

```yaml
name: Local
version: 1.0.0
schema: v1
models:
  - name: Qwen2.5-Coder 1.5B (local)
    provider: ollama
    model: qwen2.5-coder:1.5b-base
    apiBase: http://localhost:11434
    roles:
      - autocomplete
    defaultCompletionOptions:
      keepAlive: 900   # seconds the model stays loaded after the last request
```

## Rules that matter

- **Use a `-base` tag for autocomplete.** Base models do fill-in-the-middle (FIM): they see text before and after the cursor. Instruct/chat tags are for the `chat` role. Confirm with `ollama show <model>`: Capabilities must list `insert`.
- **Continue's `keepAlive` overrides Ollama's 5 min default.** Without it Continue keeps the model ~30 min. Check with `ollama ps` (UNTIL column).
- **Activity Monitor under-reports.** `llama-server` shows ~250 MB because weights are memory-mapped from disk (counted as Cached Files). Real resident use ≈ RSS (`ps -o rss= -p $(pgrep -f llama-server)`).
- Back up `config.yaml` before editing: `cp -p ~/.continue/config.yaml ~/.continue/config.yaml.bak-$(date +%Y%m%d)`.
- Large pulls on a slow link (phone hotspot ran ~100 KB/s) take hours; run them in the background and re-run the same `ollama pull` to resume.

## Switch to a different model (e.g. Qwen2.5-Coder 7B)

1. **Check it exists and its size** before pulling:
   ```bash
   curl -s https://registry.ollama.ai/v2/library/qwen2.5-coder/manifests/7b-base \
     -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
     | python3 -I -c "import json,sys; print(round(sum(l['size'] for l in json.load(sys.stdin)['layers'])/1e9,2),'GB')"
   ```
2. **Pull:** `ollama pull qwen2.5-coder:7b-base`, then `ollama show qwen2.5-coder:7b-base` (expect `insert` under Capabilities).
3. **Test FIM directly**, before touching Continue:
   ```bash
   curl -s localhost:11434/api/generate -d '{"model":"qwen2.5-coder:7b-base","prompt":"def is_prime(n):\n    ","suffix":"\n\nprint(is_prime(7))\n","stream":false,"options":{"num_predict":80,"temperature":0}}' \
     | python3 -I -c "import json,sys; r=json.load(sys.stdin); print(r['response']); print('tok/s', round(r['eval_count']/(r['eval_duration']/1e9),1))"
   ```
4. **Edit `config.yaml`:** back it up, then change `model:` (and `name:`) to the new tag. To keep both and flip quickly, keep the old entry commented out.
5. **Verify in VS Code:** type in a code or Markdown file, then:
   ```bash
   grep 'POST *"/api/generate"' /opt/homebrew/var/log/ollama.log | tail -5   # latency per suggestion
   ollama ps                                                                  # new model, SIZE, 100% GPU
   ```
6. **Compare with the 1.5B baseline** below. If the 7B is too slow or too heavy alongside WSO2 servers and Docker (24 GB machine), switch `model:` back.
7. **Free disk** for a model you no longer want: `ollama rm <tag>`.

Baseline for `qwen2.5-coder:1.5b-base` (M4 Pro, 24 GB), 45 VS Code requests: min 50 ms, median 394 ms, p90 440 ms, cold load ~1.5 s; FIM test 143 tok/s; 1.1 GB at 4K context, 1.3 GB at 8K.

## Other common changes

| Want | Do |
|---|---|
| Model unloads sooner/later | `keepAlive` in seconds under `defaultCompletionOptions` |
| Free memory now (e.g. before a load test) | `ollama stop <tag>` |
| Stop Ollama entirely / start again | `brew services stop ollama` / `brew services start ollama` |
| Add a chat model | new entry with `roles: [chat]` and an instruct tag (e.g. `qwen2.5-coder:7b-instruct`); chat is otherwise done in Claude Code |
| Disable Next Edit | `"continue.enableNextEdit": false` in VS Code settings |
| Update Ollama / Continue | `brew upgrade ollama` / `code --install-extension Continue.continue --force` |

Before changing a Continue option, check the schema shipped with the installed version: `~/.vscode/extensions/continue.continue-*/config-yaml-schema.json` (models are under `definitions.ConfigYaml.properties.models`).

## Troubleshooting: no suggestions

1. `curl -s localhost:11434/api/version` → no answer: `brew services restart ollama`, check the log tail.
2. Log shows no `/api/generate` lines while typing → Continue not sending: open the Continue panel for a config error, check `continue.enableTabAutocomplete` is not false, reload the window.
3. Requests present but status 404/500 → model tag in `config.yaml` doesn't match `ollama list`.
4. One 499 or 500 on the first request after idle is normal (client cancelled during a cold load).
5. Two ghost-text sources competing → re-check `github.copilot.enable` is all `false`.

## Remove the setup

`code --uninstall-extension Continue.continue`, `brew services stop ollama`, `brew uninstall ollama` (leaves `mlx`, `mlx-c` deps: `brew autoremove`), then delete `~/.ollama` (models) and `~/.continue`. Confirm with the user before deleting either folder.
