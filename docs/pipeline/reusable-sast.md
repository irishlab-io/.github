---
hide:
  - toc
---

# Reusable - SAST (Static Application Security Testing)

## What

This reusable workflow is an orchestrator that calls one or more individual SAST scan workflows based on the boolean flags you provide. It currently supports three scanners:

- **CodeQL** — GitHub's built-in semantic code analysis engine
- **SonarQube** — an external code quality and security platform
- **Snyk** — a developer-first security platform for open-source and code scanning

## Why

Running multiple complementary SAST tools provides deeper coverage than any single scanner alone. Centralising the dispatch logic here means consuming repositories only need to specify which tools to enable, rather than defining each scan job individually. It also makes it straightforward to add or remove scanners organisation-wide by updating a single workflow.

## How

Call this workflow and enable the desired scanners via boolean inputs. Pass the required secrets for each enabled scanner.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `codeql` | Enable CodeQL scan | No | `false` |
| `sonarqube` | Enable SonarQube scan | No | `false` |
| `snyk` | Enable Snyk scan | No | `false` |

### Secrets

| Secret | Description | Required |
|---|---|---|
| `SONAR_TOKEN` | SonarQube authentication token | Only if `sonarqube: true` |
| `SONAR_HOST_URL` | SonarQube server URL | Only if `sonarqube: true` |
| `SNYK_TOKEN` | Snyk authentication token | Only if `snyk: true` |
| `TAILSCALE_AUTHKEY` | Tailscale auth key (needed for SonarQube VPN access) | Only if `sonarqube: true` |

### Example — CodeQL only

```yaml
jobs:
  sast:
    name: SAST
    uses: irishlab-io/.github/.github/workflows/reusable-sast.yml@main
    with:
      codeql: true
```

### Example — All scanners

```yaml
jobs:
  sast:
    name: SAST
    uses: irishlab-io/.github/.github/workflows/reusable-sast.yml@main
    with:
      codeql: true
      sonarqube: true
      snyk: true
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
      SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      TAILSCALE_AUTHKEY: ${{ secrets.TAILSCALE_AUTHKEY }}
```
