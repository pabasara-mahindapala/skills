---
name: wso2-is
description: "Use when troubleshooting WSO2 Identity Server (WSO2 IS), locating configs, webapps, jar bundles, startup scripts, logs, db schema scripts, tenant artifacts, and deployment paths in Carbon-based distributions (especially 5.11.x). Keywords: wso2is, carbon, identity.xml, deployment.toml, webapps, dropins, plugins, dbscripts, startup, wso2carbon.log"
argument-hint: "Provide WSO2_IS_HOME and issue summary (startup failure, auth flow issue, db issue, deployment issue, performance)"
---

# WSO2 IS Operations Skill

## When to Use
- You need a fast map of WSO2 IS folder locations.
- You are debugging startup, login/auth, deployment, JDBC, or classloading issues.
- You need to find where to place/update webapps, OSGi bundles, and patches.
- You need correct DB schema SQL files for identity/consent/UMA/metrics.
- You need a standard triage procedure before deep debugging.

## Inputs Expected
1. `WSO2_IS_HOME` absolute path (example: `/opt/wso2is-5.11.0`)
2. Environment (local, dev, test, prod)
3. DB engine (h2/mysql/postgresql/oracle/mssql/db2)
4. Symptom + first error line

## High-Value Folder Map

### Runtime and startup
- Startup scripts:
  - `<WSO2_IS_HOME>/bin/wso2server.sh` (Linux/macOS)
  - `<WSO2_IS_HOME>/bin/wso2server.bat` (Windows)
- Utility scripts:
  - `<WSO2_IS_HOME>/bin/ciphertool.sh|.bat`
  - `<WSO2_IS_HOME>/bin/forgetme.sh|.bat`
  - `<WSO2_IS_HOME>/bin/chpasswd.sh|.bat`
  - `<WSO2_IS_HOME>/bin/carbondump.sh|.bat`
- Version/build markers:
  - `<WSO2_IS_HOME>/bin/wso2carbon-version.txt`
  - `<WSO2_IS_HOME>/bin/version.txt`

### Core configuration locations
- Main config:
  - `<WSO2_IS_HOME>/repository/conf/deployment.toml`
- Carbon/runtime config:
  - `<WSO2_IS_HOME>/repository/conf/carbon.xml`
  - `<WSO2_IS_HOME>/repository/conf/carbon.properties`
  - `<WSO2_IS_HOME>/repository/conf/log4j2.properties`
- Identity configs:
  - `<WSO2_IS_HOME>/repository/conf/identity/identity.xml`
  - `<WSO2_IS_HOME>/repository/conf/identity/identity-event.properties`
  - `<WSO2_IS_HOME>/repository/conf/identity/application-authentication.xml`
  - `<WSO2_IS_HOME>/repository/conf/identity/entitlement.properties`
- Datasource/JDBC:
  - `<WSO2_IS_HOME>/repository/conf/datasources/`
- Security/TLS:
  - `<WSO2_IS_HOME>/repository/conf/security/`
- Tomcat-level config:
  - `<WSO2_IS_HOME>/repository/conf/tomcat/`

### Deployment locations
- Webapps (WARs):
  - `<WSO2_IS_HOME>/repository/deployment/server/webapps/`
- Axis2 services/modules:
  - `<WSO2_IS_HOME>/repository/deployment/server/axis2services/`
  - `<WSO2_IS_HOME>/repository/deployment/server/axis2modules/`
- Eventing/BPM artifacts (if used):
  - `<WSO2_IS_HOME>/repository/deployment/server/eventpublishers/`
  - `<WSO2_IS_HOME>/repository/deployment/server/eventstreams/`
  - `<WSO2_IS_HOME>/repository/deployment/server/humantasks/`

### OSGi bundles, jars, and patching
- Primary OSGi bundle drop location:
  - `<WSO2_IS_HOME>/repository/components/dropins/`
- Installed plugins/bundles:
  - `<WSO2_IS_HOME>/repository/components/plugins/`
  - `<WSO2_IS_HOME>/repository/components/features/`
- Server libraries:
  - `<WSO2_IS_HOME>/repository/components/lib/`
  - `<WSO2_IS_HOME>/lib/`
- Extensions/patches:
  - `<WSO2_IS_HOME>/repository/components/extensions/`
  - `<WSO2_IS_HOME>/repository/components/patches/`
  - `<WSO2_IS_HOME>/repository/components/servicepacks/`
- Useful quick checks:
  - duplicate jar versions across `dropins/`, `plugins/`, and `lib/`
  - missing transitive jars after manual bundle updates

### Logs, temp, and runtime state
- Main logs:
  - `<WSO2_IS_HOME>/repository/logs/wso2carbon.log`
  - `<WSO2_IS_HOME>/repository/logs/audit.log`
  - `<WSO2_IS_HOME>/repository/logs/http_access_*.log`
  - `<WSO2_IS_HOME>/repository/logs/patches.log`
- PID marker:
  - `<WSO2_IS_HOME>/wso2carbon.pid`
- Runtime temp/work:
  - `<WSO2_IS_HOME>/tmp/`
  - `<WSO2_IS_HOME>/repository/data/`
  - `<WSO2_IS_HOME>/repository/database/` (embedded DB files)

### DB schema and migration scripts
- Base DB scripts root:
  - `<WSO2_IS_HOME>/dbscripts/`
  - `db2.sql`, `h2.sql`, `mysql.sql`, `postgresql.sql`, `oracle.sql`, `mssql.sql`, etc.
- Identity domain:
  - `<WSO2_IS_HOME>/dbscripts/identity/`
- Consent domain:
  - `<WSO2_IS_HOME>/dbscripts/consent/`
- UMA domain:
  - `<WSO2_IS_HOME>/dbscripts/identity/uma/`
- Metrics domain:
  - `<WSO2_IS_HOME>/dbscripts/metrics/`
- Stored procedures / cleanup:
  - `<WSO2_IS_HOME>/dbscripts/identity/stored-procedures/`
- Migration references:
  - `<WSO2_IS_HOME>/dbscripts/migrations/identity/`

### Tenant and registry resources
- Tenant content:
  - `<WSO2_IS_HOME>/repository/tenants/`
- Packaged resources:
  - `<WSO2_IS_HOME>/repository/resources/`
- Additional config artifacts:
  - `<WSO2_IS_HOME>/repository/conf/multitenancy/`

## Standard Troubleshooting Procedure
1. **Confirm startup command and version**
   - Run startup via `bin/wso2server.sh` (or `.bat`) and capture first failure stack trace.
   - Confirm version from `bin/wso2carbon-version.txt`.
2. **Read logs in order**
   - Check `repository/logs/wso2carbon.log` first.
   - Correlate with `audit.log` and `http_access_*.log` timestamps.
3. **Validate config changes**
   - Compare `repository/conf/deployment.toml` with expected environment values.
   - Review `repository/conf/identity/identity.xml` and datasource configs for syntax/values.
4. **Validate DB readiness**
   - Ensure correct schema from `dbscripts/` applied for the selected DB engine.
   - Confirm JDBC URL, username, driver, and connectivity.
5. **Validate bundles and classloading**
   - Check newly added jars in `repository/components/dropins/`.
   - Detect duplicates/conflicts with `repository/components/plugins/` and `lib/`.
6. **Validate deployed artifacts**
   - Confirm webapps are present in `repository/deployment/server/webapps/`.
   - Check for deployment scanner or extraction failures in logs.
7. **Cache/temp reset (safe environments only)**
   - Stop server cleanly.
   - Clear relevant temp/work caches in `tmp/` and selected runtime caches when needed.
   - Restart and retest.

## Quick Symptom-to-Path Guide
- Startup crash: `repository/logs/wso2carbon.log`, `repository/conf/deployment.toml`, `bin/wso2server.sh`
- Login/authn/authz issue: `repository/conf/identity/`, `repository/conf/claim-config.xml`, `repository/conf/scim2-schema-extension.config`
- JDBC or SQL errors: `repository/conf/datasources/`, `dbscripts/identity/`, `dbscripts/consent/`
- Web UI not loading: `repository/deployment/server/webapps/`, `repository/conf/tomcat/`, `repository/logs/http_access_*.log`
- Bundle resolution / `ClassNotFound`: `repository/components/dropins/`, `repository/components/plugins/`, `repository/components/lib/`
- Patch/update anomalies: `repository/components/patches/`, `repository/logs/patches.log`, `bin/wso2update_*`

## Output Expectations
When invoked, produce:
1. A short root-cause hypothesis list (max 3)
2. Exact files/folders to inspect in priority order
3. Minimal safe remediation steps
4. Verification checklist after fix

## Safety Notes
- Prefer backup before editing configs or replacing jars.
- In production, avoid deleting caches/temp without a change ticket/approval.
- Apply DB scripts only after validating DB type and version compatibility.
