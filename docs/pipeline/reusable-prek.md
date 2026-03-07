---
hide:
  - toc
---

# Reusable - Prek

## What

This reusable workflow runs [prek](https://github.com/j178/prek), a lightweight pre-commit runner, to execute pre-commit checks in CI. Like the `reusable-pre-commit` workflow it enforces hook compliance, but uses the `prek` action instead of the standard `pre-commit/action`.

## Why

`prek` provides a fast, minimal alternative to the full `pre-commit` toolchain while remaining compatible with `.pre-commit-config.yaml`. Using it in CI ensures the same linting and formatting gates apply even when repositories opt for a leaner hook runner. The workflow uses `continue-on-error: true` so findings are surfaced as warnings rather than hard failures, giving teams time to triage.

!!! note
    A failure in the pre-commit checks will produce a visible CI error annotation but will not block the pipeline. Teams should address all findings before merging.

## How

Call this workflow from any repository that has a `.pre-commit-config.yaml` file.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `skips` | Comma-separated list of hook IDs to skip (maps to the `SKIP` environment variable) | No | `""` |

### Secrets

None required.

### Example

```yaml
jobs:
  prek:
    name: Prek Pre-Commit
    uses: irishlab-io/.github/.github/workflows/reusable-prek.yml@main
    with:
      skips: "pytest,uv-export"
```
