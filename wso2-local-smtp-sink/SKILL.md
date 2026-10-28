---
name: wso2-local-smtp-sink
description: Set up a local SMTP server (sink, default 127.0.0.1:2525) and configure a local WSO2 Identity Server to send all its email to it, so every mail IS sends is captured as an .eml file you can list, read, and extract links/codes from. Use for any local IS work that needs outbound email to work or be inspected. Standard-library Python only, no real mail server or internet needed.
argument-hint: <IS_HOME> <mail-output-dir> [port]
---

# Local SMTP server for WSO2 Identity Server

Gives a local IS a working SMTP server. Every mail IS sends, for any feature and any tenant using the server-level email settings, is saved as one `.eml` file. Nothing is delivered anywhere.

Script: `~/.claude/skills/wso2-local-smtp-sink/scripts/smtp_sink.py`. Standard library only, no TLS, accepts any AUTH, never relays. For local environments only: never point a customer or shared server at it.

Arguments: `$ARGUMENTS` → `IS_HOME`, `OUTDIR`, optional `PORT` (default `2525`).

## 1. Choose where mails are saved

Keep the mails with the work they belong to, e.g. `<case-dir>/products/iam/test-materials/mails`. Don't use a scratch or tmp dir, which can be wiped between turns.

## 2. Start the SMTP server

```bash
S=~/.claude/skills/wso2-local-smtp-sink/scripts/smtp_sink.py
OUT=<OUTDIR>
PORT=2525
nohup python3 -I "$S" serve "$OUT" --port "$PORT" > "$OUT.log" 2>&1 &
echo $! > "$OUT.pid"
```

Check that it's up: `cat "$OUT.log"` should show `smtp-sink listening on 127.0.0.1:2525 ...`.

Optional check that it's working, before involving IS:

```bash
python3 -I -c "import smtplib; smtplib.SMTP('127.0.0.1', $PORT).sendmail('a@test', ['b@test'], 'Subject: sink check\n\nhello')"
python3 -I "$S" list "$OUT"
```

## 3. Configure IS to use it

Back up `<IS_HOME>/repository/conf/deployment.toml`, then add this table. If an `[output_adapter.email]` table already exists, edit it instead: a second copy of the table breaks TOML parsing.

```toml
[output_adapter.email]
from_address = "wso2is@example.test"
username = "dummy"
password = "dummy"
hostname = "localhost"
port = 2525
enable_start_tls = false
enable_authentication = false
```

- `enable_start_tls = false` is required because the sink refuses STARTTLS.
- `username` and `password` aren't used while authentication is off, but keep them non-empty.
- Change `port` if you started the sink on another port.

**Restart IS** after editing deployment.toml.

These keys were checked in the `output-event-adapters.xml.j2` template and `default.json` of IS **5.10.0, 6.1.0, 7.2.0 and 7.3.0**, and are the same in all four. For any other version, confirm them in `<IS_HOME>/repository/resources/conf/templates/repository/conf/output-event-adapters.xml.j2` first.

IS only sends a mail when the feature that sends it is enabled. That's a separate setting per feature, configured for whatever you are testing. This skill only makes sure that mails IS does send arrive in `OUTDIR`.

## 4. Read captured mail

```bash
python3 -I "$S" list  "$OUT"          # one line per mail: file, recipients, subject
python3 -I "$S" show  "$OUT" [FILE]   # decoded headers and body (newest mail if FILE is omitted)
python3 -I "$S" links "$OUT" [FILE]   # every URL in the body (confirmation links etc.)
```

- **Was a mail sent for an action?** Count `ls "$OUT"/*.eml | wc -l` before and after it, and wait about 3 s after the action because IS sends asynchronously.
- **Who was it sent to?** The `list` output, or the `X-Sink-Rcpt:` header in the `.eml` file.
- **Codes or OTPs that aren't links:** use `show`, then `grep` the output.

## Troubleshooting

| Symptom | Check |
|---|---|
| Nothing in `$OUT.log` after the action | The feature that should send the mail may be disabled or decided not to send (some flows silently skip sending, e.g. for unknown users). Check `grep -i -E "EmailEventAdapter\|smtp\|MessagingException" <IS_HOME>/repository/logs/wso2carbon.log`. Confirm the deployment.toml port matches `--port` and that IS was restarted. |
| `MessagingException` / STARTTLS error in the IS log | `enable_start_tls` is still `true`. |
| `Connection refused` in the IS log | The sink isn't running (`cat "$OUT.log"`), or the host or port is wrong. |
| Startup log shows `Event Publisher deployment held back ... EmailPublisher.xml ... Stream ... does not exist` | Normal at startup. The publisher activates once its stream is deployed. |
| `Address already in use` when starting the sink | A sink is already on that port. Reuse it, or pick another `--port` and update deployment.toml. |
| IS 7.x: mails for one tenant don't arrive while others do | That tenant may have its own email provider set in the Console, which this server-level config doesn't cover. Check the tenant's email provider settings. |

## Stop and clean up

1. `kill "$(cat "$OUT.pid")"`. Don't use `pkill -f smtp_sink`: the pattern also matches the shell running the command and kills it.
2. Restore the backed-up `deployment.toml` and restart IS.
3. Captured mail can contain live links, codes, or credentials. Delete `$OUT` when you're done.
