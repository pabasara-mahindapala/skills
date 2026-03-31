---
name: wso2-security-scan
description: "Use when analyzing security vulnerability reports or advisories for WSO2 IS runtimes or Docker images. Covers CVE/GHSA reports from SCA tools (Trivy, Grype, Snyk), supply chain advisories, threat intel notices, and any case where a vulnerability needs to be checked against a WSO2 IS installation — with or without a CVE number. Keywords: CVE, GHSA, security scan, Trivy, Grype, Snyk, SCA, vulnerability, docker image, supply chain, advisory, npm, jackson, zookeeper, solr, go stdlib"
argument-hint: "Provide the product version/update level, the vulnerability or advisory details (CVE/GHSA if available, or a description of affected components/versions), and whether you are targeting a Docker image or a local runtime installation"
---

# WSO2 Product Security Vulnerability Scan Skill

## When to Use
- CVEs or GHSAs from a Docker image security scan (Trivy, Grype, Snyk, or similar SCA tools).
- Security advisories or threat intel notices **without a CVE number** (e.g. supply chain compromises, hijacked packages, zero-days, vendor bulletins).
- You need to locate a vulnerable component inside a WSO2 IS runtime — whether a Docker image, a local product distribution, or a deployed installation.
- You need to assess whether a reported issue is actually present and exploitable in the context of WSO2 IS.

## Determining the Scan Target

WSO2 IS can be scanned in two ways depending on what is available:

| Target | When to use |
|---|---|
| **Local runtime / distribution directory** | A `wso2is-x.x.x` directory is available on disk (e.g. from a local cluster, a mounted volume, or an extracted pack) |
| **Docker image** | No local directory; pull from `registry.wso2.com` (see Step 1 below) |

Always prefer scanning the local runtime if it is available — it reflects the exact deployed state. Ask the user for the `WSO2_IS_HOME` path before pulling a Docker image unnecessarily.

## Step 1 — Identify the Vulnerability Type

Before searching, classify what you are looking for. This determines the search strategy.

| Vulnerability type | Examples | Search approach |
|---|---|---|
| Java library CVE | jackson-core DoS, ZooKeeper credential leak | JAR search (direct + nested) |
| Go binary CVE | Go stdlib net/url, crypto/tls | `go version -m` on update tool binary |
| NPM/JS supply chain | Compromised axios, malicious package (may or may not have a CVE) | Search for `node_modules`, lock files, bundled JS chunks |
| Config/behaviour advisory | Default credentials, insecure defaults | Check config files and deployment descriptors |
| Disk artifact / RAT indicator | Malware dropped to known paths | Check IOC paths directly on the filesystem |

For advisories without a CVE, extract the key facts from the notice: **affected package name**, **affected versions**, and any **indicator of compromise (IOC)** paths or file names provided.

## Step 2 — Access the Runtime

### Option A — Local distribution (preferred)
If the user provides a path, use it directly as `WSO2_IS_HOME`. No Docker pull needed.

### Option B — Docker image
WSO2 Docker images are hosted at `registry.wso2.com`. You need a **CLI Secret** from the WSO2 Support Portal:

> **Support Portal → Projects → My Projects → Registry Tokens → Generate Token**

Read credentials from the `.env` file, then login:
```bash
docker login registry.wso2.com -u '<WSO2_email>' -p '<CLI_Secret>'
docker pull registry.wso2.com/wso2-is/is:<version>-alpine-jdk8
```

## Step 3 — Locate the Vulnerable Component

### Java library CVE — Direct JAR search
```bash
find <WSO2_IS_HOME> -name "*<library>*" 2>/dev/null | sort
```

### Java library CVE — Nested JAR search (jar-in-jar — always run this)
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

### NPM / JavaScript supply chain advisory (CVE or no CVE)
WSO2 IS 5.11.0 is a Java application and **does not use NPM at runtime**. However, the React-based Console and MyAccount webapps ship pre-compiled webpack bundles that may embed JavaScript libraries. Check:

**1. Is NPM used at all in the distribution?**
```bash
# No node_modules or lock files = npm never ran here; bundled JS only
find <WSO2_IS_HOME> -type d -name "node_modules" 2>/dev/null
find <WSO2_IS_HOME> -type f \( -name "package.json" -o -name "package-lock.json" \
  -o -name "yarn.lock" -o -name "pnpm-lock.yaml" \) 2>/dev/null
```

**2. Do the affected package/version strings appear in the distribution?**
```bash
grep -r "<package-name>" <WSO2_IS_HOME> --include="*.json" \
  --include="*.yaml" --include="*.lock" -l 2>/dev/null
# Also check bundled JS chunks for exact version strings
grep -r "<affected-version>" <WSO2_IS_HOME> --include="*.js" 2>/dev/null | head -20
```

**3. Check for IOC artifacts on disk** (paths provided in the advisory):
```bash
# Example for a macOS RAT dropper — substitute paths from the advisory
ls -la /Library/Caches/<artifact> 2>/dev/null && echo "COMPROMISED" || echo "clean"
ls -la /tmp/<artifact> 2>/dev/null && echo "COMPROMISED" || echo "clean"
```

**Key point:** If no `node_modules` directory and no lock files exist in the distribution, and the malicious version string does not appear literally in any bundled JS file, the installation is **not affected** — WSO2 did not run `npm install` with a compromised package. Check the bundle file timestamps against the attack window as a final confirmation.

## Step 4 — Assess Actual Exploitability

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
