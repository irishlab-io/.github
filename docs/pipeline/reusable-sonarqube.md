---
hide:
  - toc
---

# Reusable - SonarQube Scan

## What

This reusable workflow runs a [SonarQube](https://www.sonarqube.org/) static analysis scan against the repository and optionally enforces a Quality Gate. It first connects to a private SonarQube instance over a [Tailscale](https://tailscale.com/) VPN tunnel before running the scan, making it suitable for self-hosted SonarQube servers that are not publicly accessible.

## Why

SonarQube provides deep code quality and security analysis including code smells, bugs, vulnerabilities, and technical debt metrics. The Quality Gate feature blocks merges when the codebase falls below configured thresholds, preventing the gradual accumulation of quality and security issues. Using Tailscale ensures the scanner can reach an on-premises SonarQube instance securely without exposing it to the internet.

## How

Call this workflow from any repository whose SonarQube project has been provisioned and whose credentials are available as secrets.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `sonarqube_gating` | Enforce the SonarQube Quality Gate (fail the job if gate fails) | No | `true` |

### Secrets

| Secret | Description | Required |
|---|---|---|
| `TAILSCALE_AUTHKEY` | Tailscale auth key used to join the private tailnet | Yes |
| `SONAR_TOKEN` | SonarQube authentication token | Yes |
| `SONAR_HOST_URL` | URL of the SonarQube server | Yes |

### Prerequisites

- A SonarQube project configured for the repository with a valid `sonar-project.properties` or inline configuration
- The SonarQube server reachable from the Tailscale tailnet
- A machine tagged `tag:ci` in the tailnet policy

### Example

```yaml
jobs:
  sonarqube:
    name: SonarQube Scan
    uses: irishlab-io/.github/.github/workflows/reusable-sonarqube.yml@main
    with:
      sonarqube_gating: true
    secrets:
      TAILSCALE_AUTHKEY: ${{ secrets.TAILSCALE_AUTHKEY }}
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```
