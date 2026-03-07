---
hide:
  - toc
---

# Reusable - GitGuardian Secret Scan

## What

This reusable workflow runs [GitGuardian](https://www.gitguardian.com/) secret scanning using [ggshield](https://github.com/GitGuardian/ggshield) to detect secrets, API keys, credentials, and other sensitive data committed to the repository.

## Why

Accidentally committing secrets is one of the most common and dangerous security mistakes. GitGuardian scans every push and pull request against a library of over 400 secret detectors and alerts the team before a secret can be exploited. Running this scan automatically in CI closes the gap between a commit and detection.

!!! note
    This workflow uses `continue-on-error: true` so that a detected secret produces a visible warning without blocking the pipeline. Teams should treat any finding as a mandatory remediation item and rotate any exposed credentials immediately.

## How

Call this workflow from any repository that has a GitGuardian account and API key configured as an organisation or repository secret.

### Inputs

None.

### Secrets

| Secret | Description | Required |
|---|---|---|
| `GITGUARDIAN_API_KEY` | API key for authenticating with the GitGuardian service | Yes |

### Example

```yaml
jobs:
  secret-scan:
    name: GitGuardian Scan
    uses: irishlab-io/.github/.github/workflows/reusable-gitguardian.yml@main
    secrets:
      GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}
```
