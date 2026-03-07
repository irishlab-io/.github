---
hide:
  - toc
---

# Reusable - Snyk Scan

## What

This reusable workflow runs [Snyk](https://snyk.io/) to scan the repository's Node.js dependencies for known vulnerabilities. It checks all packages against Snyk's vulnerability database and fails the job if any issue at or above the configured severity threshold is found.

## Why

Open-source dependencies are a common attack surface. Snyk continuously monitors packages for new CVEs and provides actionable fix advice. Running Snyk automatically in CI ensures that vulnerable dependencies are caught before they reach production and that the team is alerted as soon as a new CVE is published for a package already in use.

## How

Call this workflow from any Node.js repository that has a Snyk account and token configured as a secret.

### Inputs

None.

### Secrets

| Secret | Description | Required |
|---|---|---|
| `SNYK_TOKEN` | Snyk authentication token | Yes |

### Configuration

The scan runs with `--severity-threshold=high`, meaning only `high` and `critical` vulnerabilities will cause the job to fail. To change this threshold, override the workflow or contact the platform team.

### Example

```yaml
jobs:
  snyk:
    name: Snyk Vulnerability Scan
    uses: irishlab-io/.github/.github/workflows/reusable-snyk.yml@main
    secrets:
      SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```
