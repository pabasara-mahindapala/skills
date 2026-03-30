---
name: wso2-security-scan
description: "Use when analyzing SCA (Software Composition Analysis) vulnerability reports for WSO2 product Docker images. Covers pulling images from registry.wso2.com, locating vulnerable components including nested JARs, and assessing actual exploitability. Keywords: CVE, GHSA, security scan, Trivy, Grype, Snyk, SCA, vulnerability, docker image, jackson, zookeeper, solr, go stdlib"
argument-hint: "Provide case ID, product version, Docker image tag, and the list of CVEs/GHSAs from the scan report"
---

# WSO2 Product Security Vulnerability Scan Skill

## When to Use
- Customer reports CVEs from a Docker image security scan (Trivy, Grype, Snyk, or similar SCA tools).
- You need to locate a vulnerable component inside a WSO2 product Docker image.
- You need to assess whether a flagged CVE is actually exploitable in the context of WSO2 IS.

## Step 1 — Pull the WSO2 Docker Image

WSO2 Docker images are hosted at `registry.wso2.com`. Standard WSO2 account credentials do not work — you need a **CLI Secret** from the WSO2 Support Portal:

> **Support Portal → Projects → My Projects → Registry Tokens → Generate Token**

Read credentials from the `.env` file, then login:
```bash
docker login registry.wso2.com -u '<WSO2_email>' -p '<CLI_Secret>'
docker pull registry.wso2.com/wso2-is/is:<version>-alpine-jdk8
```

## Step 2 — Locate the Vulnerable Component

### Direct JAR search
```bash
find <WSO2_IS_HOME> -name "*<library>*" 2>/dev/null | sort
```

### Nested JAR search (jar-in-jar — always run this)
SCA scanners detect JARs embedded inside OSGi bundles. A `pom.xml` text search alone misses these because the nested JAR may not be declared as a Maven dependency in the outer JAR's pom.

```bash
find <WSO2_IS_HOME> -name "*.jar" | while read jar; do
  jar tf "$jar" 2>/dev/null | grep -i "\.jar$" | while read nested; do
    echo "$jar → $nested"
  done
done | grep -i "<library>"
```

**Real example:** `zookeeper-3.9.4.jar` is embedded inside `solr_8.11.1.wso2v18.jar` at `repository/components/plugins/`. It does not appear as a standalone file anywhere in the image.

### Go binary vulnerability (stdlib CVEs)
The `bin/wso2update_linux` binary is the WSO2 U2 Update Tool, compiled with Go. Go stdlib CVEs (e.g. `net/url`, `crypto/tls`) will be flagged against this binary:
```bash
go version -m <WSO2_IS_HOME>/bin/wso2update_linux 2>/dev/null | grep "^go"
```
This binary is **not a runtime service** — it only runs during administrator-initiated update windows.

## Step 3 — Assess Actual Exploitability

| Component | Typical CVE Type | WSO2 IS Risk Assessment |
|---|---|---|
| ZooKeeper inside Solr | Credential logging, hostname bypass | Low — WSO2 IS uses Solr in standalone mode, ZooKeeper ensemble features inactive |
| jackson-core async parser | DoS via unbounded number parsing | Low — WSO2 IS uses synchronous Tomcat/CXF, async parser code path not exercised |
| wso2update_linux (Go) | stdlib net/url, crypto CVEs | Low — not a running service, admin-only execution context |

## Known Component Locations for Common SCA Hits

| Flagged Library | Location in Product |
|---|---|
| ZooKeeper (nested in Solr) | `repository/components/plugins/solr_*.jar` → `zookeeper-*.jar` |
| jackson-core | `repository/components/lib/jackson-core-*.jar`, `lib/runtimes/cxf3/` |
| WSO2 Update Tool (Go) | `bin/wso2update_linux` / `bin/wso2update_darwin` |
| Kafka adapter | `repository/components/plugins/org.wso2.carbon.event.output.adapter.kafka_*.jar` |
