---
hide:
  - toc
---

# Reusable - Secret Scan (GitGuardian)

## What

This reusable workflow runs [GitGuardian](https://www.gitguardian.com/) secret scanning using [ggshield](https://github.com/GitGuardian/ggshield) to detect secrets, API keys, passwords, and other sensitive data that may have been committed to the repository.

!!! note
    This workflow is functionally equivalent to [`reusable-gitguardian`](reusable-gitguardian.md) but runs the scan **without** the `continue-on-error` safety net, causing the job to **fail** immediately if a secret is detected.

## Why

Accidentally committing secrets is one of the most common and dangerous security mistakes. GitGuardian scans every push and pull request against a library of over 400 secret detectors and blocks the pipeline if a secret is found, forcing remediation before the code can progress. This hard-failure mode is appropriate for pipelines where secret exposure must be treated as a blocking issue.

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
    name: Secret Scan
    uses: irishlab-io/.github/.github/workflows/reusable-secret.yml@main
    secrets:
      GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}
```
