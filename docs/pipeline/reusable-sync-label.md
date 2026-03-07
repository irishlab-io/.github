---
hide:
  - toc
---

# Reusable - Sync Label

## What

This reusable workflow synchronises a repository's GitHub labels with the definitions in `.github/labels.yml`. It uses [EndBug/label-sync](https://github.com/EndBug/label-sync) and a GitHub App token to update, create, or delete labels so that the repository's label set always matches the file on disk.

## Why

Label drift — where labels in GitHub diverge from what is defined in configuration — makes triage inconsistent across repositories. Automating label synchronisation ensures every repository in the organisation shares the same label taxonomy, colours, and descriptions, which is especially important when labels are used to drive automation (e.g. release notes, labeler rules, project boards).

## How

This workflow can be triggered manually (`workflow_dispatch`) or called from another workflow (`workflow_call`). It requires a GitHub App with sufficient permissions to manage labels.

### Inputs

None.

### Secrets

The workflow reads the following secrets from the calling environment (configured at the organisation level):

| Secret | Description | Required |
|---|---|---|
| `IRISHLAB_BOT_APP_ID` | GitHub App ID used to generate an installation token | Yes |
| `IRISHLAB_BOT_PRIVATE_KEY` | Private key for the GitHub App | Yes |

### Prerequisites

- A `.github/labels.yml` file in the repository listing all desired labels
- The `IRISHLAB_BOT_APP_ID` and `IRISHLAB_BOT_PRIVATE_KEY` secrets available in the repository or organisation

### Example

```yaml
on:
  push:
    paths:
      - ".github/labels.yml"

jobs:
  sync-labels:
    name: Sync Labels
    uses: irishlab-io/.github/.github/workflows/reusable-sync-label.yml@main
    secrets: inherit
```
