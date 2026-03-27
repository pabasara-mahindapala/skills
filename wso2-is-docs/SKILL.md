---
name: wso2-is-docs
description: Search the local WSO2 Identity Server documentation repository for product knowledge to support issue analysis or solution building.
---

# WSO2 IS Documentation Search

Search the local WSO2 Identity Server documentation repository for product knowledge to support issue analysis or solution building.

## Step 1 — Sync the docs repo

Check if the docs-is repo exists locally. The expected clone location is `~/Documents/GitHub/wso2/docs-is`.

Run this to sync:

```bash
if [ -d "$HOME/Documents/GitHub/wso2/docs-is/.git" ]; then
  git -C "$HOME/Documents/GitHub/wso2/docs-is" pull origin master
else
  git clone https://github.com/wso2/docs-is.git "$HOME/Documents/GitHub/wso2/docs-is"
fi
```

If the clone or pull fails (e.g. network unavailable), fall back to whatever existing local state.

## Step 2 — Locate the right version directory

Docs are versioned under:
```
~/Documents/GitHub/wso2/docs-is/en/identity-server/
  5.9.0/
  5.10.0/
  5.11.0/
  6.0.0/
  6.1.0/
  7.0.0/
  7.1.0/
  7.2.0/
  next/        ← unreleased/upcoming version
```

Match the customer's product version to the closest directory. If the exact version is not present, use the nearest available (prefer the same major.minor). For unreleased/latest work, use `next/`.

The root for a given version's content is:
```
~/Documents/GitHub/wso2/docs-is/en/identity-server/<version>/docs/
```

## Step 3 — Navigate the docs structure

Each version's `docs/` directory follows this layout:

```
docs/
  apis/              # REST API reference pages (one .md per API)
  concepts/          # High-level product concepts (customer-iam, workforce-iam, basic-concepts, etc.)
  guides/            # How-to guides, organized by topic:
    account-configurations/
    analytics/
    applications/
    authentication/
    authorization/
    branding/
    identity-verification/
    multitenancy/
    notification-channels/
    organization-management/
    service-extensions/
    user-self-service/
    users/
    your-is/
  references/        # Configuration references, deprecation notices, architecture docs
    wso2-identity-server-feature-deprecation.md   ← deprecation lifecycle table
    about-this-release.md                          ← release notes (not always present)
    extend/          # Extension/customization reference docs
    concepts/        # Architecture and design concepts
  complete-guides/   # End-to-end scenario walkthroughs
  connectors/        # Connector-specific docs
  integrations/      # Third-party integration guides
  quick-starts/      # Quick start tutorials
  sdks/              # SDK guides
  deploy/            # Deployment and infrastructure guides
```

Older versions (5.x, 6.x) use a slightly different layout under `docs/`:
```
docs/
  learn/             # How-to guides (equivalent to guides/ in 7.x)
  develop/           # Developer/API docs (equivalent to apis/ in 7.x)
  get-started/       # Architecture and concepts
  references/        # Config references and release notes
  setup/             # Installation and deployment
  administer/        # Administration guides
```

## Step 4 — Search and read

Use `Grep` to search across the relevant version's docs for keywords related to the topic. Then read the matching files with the `Read` tool.

**Useful search patterns:**
- Feature name or API name (e.g. `SCIM 2.0`, `TOTP`, `OAuth2`)
- Config property (e.g. `enable_scim2`, `identity_mgt`)
- Error keyword or exception class name
- Endpoint path (e.g. `/scim2/Users`)

**High-value files to check for any topic:**
- `references/about-this-release.md` — what changed in this version
- `apis/<feature>-rest-api.md` — REST API details
- `guides/<topic>/` — configuration and how-to steps

## Step 5 — Apply the findings

Incorporate the documentation findings into your analysis:
- Cite the version-specific doc path when referencing behaviour or configuration
- Note any discrepancies between the docs and observed behaviour (e.g. if a config property is documented but not present in the product, or vice versa)
- Cross-reference with source code and GitHub issues for a complete picture
