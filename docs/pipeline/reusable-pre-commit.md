---
hide:
  - toc
---

# Reusable - Pre-Commit

## What

This reusable workflow installs [pre-commit](https://pre-commit.com/) and runs all configured hooks against the repository. It caches the hook environments keyed on the Python version and `.pre-commit-config.yaml` hash to keep runs fast.

## Why

Pre-commit hooks enforce code quality, formatting, linting, and security checks before code is merged. Running the same hooks in CI as developers run locally guarantees that no commit bypasses the checks (e.g. via `--no-verify`) and that the entire team works to the same standards, regardless of local tooling differences.

## How

Call this workflow from any repository that has a `.pre-commit-config.yaml` file.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `configuration_file` | Extra arguments passed to `pre-commit run` (e.g. a specific hook ID or `--all-files`) | No | `""` |
| `skips` | Comma-separated list of hook IDs to skip (maps to the `SKIP` environment variable) | No | `"true"` |

### Secrets

None required.

### Example

```yaml
jobs:
  pre-commit:
    name: Pre-Commit Checks
    uses: irishlab-io/.github/.github/workflows/reusable-pre-commit.yml@main
    with:
      skips: "pytest,uv-export"
```
