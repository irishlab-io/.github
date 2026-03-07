---
hide:
  - toc
---

# Reusable - GH Labeler

## What

This reusable workflow automatically applies labels to pull requests based on the files changed, using [actions/labeler](https://github.com/actions/labeler). It also synchronises the repository's label definitions to ensure the label set stays consistent with the configuration file.

## Why

Manual labelling of PRs is error-prone and time-consuming. Automating it ensures that every PR is consistently categorised (e.g. `frontend`, `backend`, `infra`, `docs`) based on the paths of changed files, making triage and filtering much easier across large repositories.

## How

Call this workflow on pull request events from any repository that has a `.github/labeler.yml` and `.github/labels.yml` configuration.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `configuration_file` | Path to the labeler configuration file | No | `.github/labeler.yml` |

### Secrets

None required.

### Prerequisites

- A `.github/labeler.yml` file defining path-to-label mappings
- A `.github/labels.yml` file listing all labels to sync

### Example

```yaml
on:
  pull_request:

jobs:
  labeler:
    name: Label PR
    uses: irishlab-io/.github/.github/workflows/reusable-gh-labeler.yml@main
    with:
      configuration_file: ".github/labeler.yml"
```
