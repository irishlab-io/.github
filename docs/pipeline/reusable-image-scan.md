---
hide:
  - toc
---

# Reusable - Trivy Image Scan

## What

This reusable workflow scans a Docker container image for known vulnerabilities using [Trivy](https://github.com/aquasecurity/trivy). Scan results are produced in SARIF format and uploaded to the **GitHub Security** tab for centralised visibility.

## Why

Container images aggregate OS packages and language libraries, both of which can contain known CVEs. Scanning images automatically in CI — especially after a build — ensures vulnerabilities are surfaced before images are deployed to any environment. Uploading results to GitHub Security provides a persistent, auditable record of the security posture of every image version.

## How

Call this workflow after a Docker build step, passing the image reference that was just produced.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `image` | Full image reference to scan (e.g. `ghcr.io/org/repo:tag`) | Yes | — |
| `exit-code` | Set to `1` to fail the job when CVEs are found | No | `0` |
| `severity` | Comma-separated list of severities to report | No | `HIGH,CRITICAL` |
| `ignore-unfixed` | Skip vulnerabilities that have no available fix | No | `true` |

### Secrets

None required.

### Required Permissions

```yaml
permissions: read-all
```

### Example

```yaml
jobs:
  image-scan:
    name: Trivy Image Scan
    uses: irishlab-io/.github/.github/workflows/reusable-image-scan.yml@main
    with:
      image: "ghcr.io/my-org/my-app:latest"
      severity: "HIGH,CRITICAL"
      exit-code: "0"
    permissions:
      contents: read
      security-events: write
```
