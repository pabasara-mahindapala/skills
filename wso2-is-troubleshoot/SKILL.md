---
name: wso2-is-troubleshoot
description: "Use when troubleshooting WSO2 Identity Server issues — login failures, token exchange errors, adaptive auth script tracing, federated IdP auth, correlation ID analysis, audit log events, HTTP access log correlation. Keywords: authorization code, oauth2, oidc, adaptive auth, saml, token, login not working"
argument-hint: "Provide logs around the failed login"
---

# WSO2 IS Authorization Code Flow Troubleshooting

## When to Use
- A customer reports "login not working" on an OIDC/OAuth2 authorization code flow.
- You need to correlate audit log events, carbon log adaptive auth traces, and HTTP access logs.
- You need to identify where in the flow (identifier step, federated auth, claim resolution, token exchange) the failure occurred.

## Correlating the Three Sources

Always correlate these three sources in order:

### 1. IS audit log (`audit.log`) — per-session correlation ID
Use the correlation ID to trace the full session. Key events to look for in sequence:

| Audit event examples | Description |
|---|---|
| `LoginStepSuccess` (Step 1, `LOCAL`, `IdentifierExecutor`) | User entered their identifier; IS accepted it |
| `LoginStepSuccess` (Step 2, federated IdP, `SAMLSSOAuthenticator`) | Federated auth completed; note `AuthenticatedIdP`, `UserStoreDomain` etc. |
| `Get-User-List` by `http://wso2.org/claims/username` | IS resolved the federated subject to a local user |
| `Get-User-Claim-Values` Target=`DOMAIN/username` | Claims retrieved for token building |
| `Set-User-Claim-Values` Target=`DOMAIN/username` | Post-auth claim updates (e.g. `lastLoginTime`) |
| `Login` (final) `Result: Success` | Full authentication completed — auth code about to be issued |

### 2. IS carbon log (`wso2carbon.log`) — adaptive auth script tracing
Look for `JsLogger` lines which are `Log` calls from the adaptive authentication script.

### 3. HTTP access log + HAR — end-to-end browser flow proof
Cross-reference the auth code value between HAR and access log to confirm the full round-trip:

```
HAR entry N:   GET /oauth2/authorize?sessionDataKey=X  → 302
HAR entry N+1: GET <app-redirect-uri>?code=<CODE>&state=...  → 302
access.log:    POST /oauth2/token?code=<CODE>&grant_type=authorization_code  → 200 <bytes>
```

If the token endpoint returns **200**, the authorization code was valid and tokens were issued. The login completed from IS's perspective. If the app then fails, the issue is in the application layer, not IS.

## Common Response Codes

| Endpoint | Status | Meaning |
|---|---|---|
| `POST /commonauth` | 302 | Step processed; redirecting to next step or IdP |
| `GET /oauth2/authorize` | 302 | Auth code issued; redirecting to `redirect_uri` |
| `POST /oauth2/token` | 200 | Token exchange successful |
| `POST /oauth2/token` | 400 | Bad request — code expired, already used, or `redirect_uri` mismatch |
| `GET /oauth2/userinfo` | 401 | Access token expired or invalid |
| `GET /authenticationendpoint/login.do` | 200 | Login page served (session still at identifier/password step) |

## Output Expectations
1. Where in the flow the failure occurred (which step/event)
2. Root-cause hypothesis (max 3)
3. Exact log lines or audit events that confirm the hypothesis
4. Minimal remediation steps and verification checklist
