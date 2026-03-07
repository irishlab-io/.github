---
hide:
  - toc
---

# Reusable - Ensure SHA Pinned Actions

## What

This reusable workflow verifies that every GitHub Actions step in the repository pins its action by a full commit SHA rather than a mutable tag (e.g. `@v1`). It uses [zgosalvez/github-actions-ensure-sha-pinned-actions](https://github.com/zgosalvez/github-actions-ensure-sha-pinned-actions) to perform the check.

## Why

Using mutable tags like `@v1` or `@main` in workflow steps exposes pipelines to supply-chain attacks: a malicious update to a tag can silently compromise CI. Pinning actions to a specific commit SHA ensures that the exact, audited code is always executed, regardless of upstream changes. This is a [recommended security hardening practice](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions) from GitHub.

## How

Call this workflow from any repository where you want to enforce SHA pinning of all referenced Actions.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `allowlist` | Newline-separated list of action owner prefixes that are exempt from pinning (e.g. internal org actions) | No | `"${{ github.repository_owner }}/"` |

### Secrets

None required.

### Example

```yaml
jobs:
  pin-actions:
    name: Ensure SHA Pinned Actions
    uses: irishlab-io/.github/.github/workflows/reusable-gh-pin-actions.yml@main
    with:
      allowlist: |
        "my-org/"
```
