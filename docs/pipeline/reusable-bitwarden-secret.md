---
hide:
  - toc
---

# Reusable - Bitwarden Secret Sync

## What

This reusable workflow pulls secrets from [Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/) and provisions them as GitHub secrets at the **organisation** or **repository** level.

It can be called standalone from any workflow, or it is invoked automatically by the [Repository Creation](repo-onboarding.md) pipeline when a `repos/*.yml` config file declares a `secrets` block.

A companion **rotation workflow** (`reusable-bitwarden-secret-rotation.yml`) scans all `repos/*.yml` files and re-syncs every declared secret on a daily schedule, ensuring GitHub secrets stay in sync whenever a value changes in the vault.

## Why

Maintaining secrets in Bitwarden Secrets Manager provides a single source of truth for credentials shared across repositories and teams. Syncing them into GitHub automatically at repository-creation time removes the manual step of copying values into the GitHub UI and eliminates the risk of secrets drifting out of sync. The scheduled rotation ensures that any update made in the Bitwarden vault is automatically propagated to all consuming GitHub secrets without manual intervention.

## How

### Prerequisites

The following org-level secrets must be configured before calling this workflow:

| Secret | Description |
|---|---|
| `BW_ACCESS_TOKEN` | Bitwarden Secrets Manager machine account access token |
| `IRISHLAB_BOT_APP_ID` | GitHub App ID used to create the scoped token |
| `IRISHLAB_BOT_PRIVATE_KEY` | GitHub App private key for token generation |

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `org_secrets` | Newline-separated list of Bitwarden → GitHub secret mappings for **org-level** secrets. Format per line: `<bitwarden-uuid> > GITHUB_SECRET_NAME` | No | `""` |
| `repo_secrets` | Newline-separated list of Bitwarden → GitHub secret mappings for **repo-level** secrets. Format per line: `<bitwarden-uuid> > GITHUB_SECRET_NAME` | No | `""` |
| `repo_name` | Target repository name (without owner). Required when `repo_secrets` is provided. | No | `""` |

### Secrets

| Secret | Description | Required |
|---|---|---|
| `BW_ACCESS_TOKEN` | Bitwarden Secrets Manager machine account access token | Yes |
| `IRISHLAB_BOT_APP_ID` | GitHub App ID for bot authentication | Yes |
| `IRISHLAB_BOT_PRIVATE_KEY` | GitHub App private key for bot authentication | Yes |

### Example — standalone call from another workflow

```yaml
jobs:
  sync-secrets:
    name: Sync Bitwarden Secrets
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret.yml@main
    with:
      org_secrets: |
        11111111-1111-1111-1111-111111111111 > DATADOG_API_KEY
        22222222-2222-2222-2222-222222222222 > SONARQUBE_TOKEN
      repo_secrets: |
        33333333-3333-3333-3333-333333333333 > DATABASE_URL
      repo_name: svc-payments-api
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
      IRISHLAB_BOT_APP_ID: ${{ secrets.IRISHLAB_BOT_APP_ID }}
      IRISHLAB_BOT_PRIVATE_KEY: ${{ secrets.IRISHLAB_BOT_PRIVATE_KEY }}
```

### Example — declaring secrets in a repo config file

When a repository is created via the `repos/*.yml` automation, add a `secrets` block to the config file to have Bitwarden secrets provisioned automatically:

```yaml
# repos/svc-payments-api.yml
name: svc-payments-api
description: Payments API service
visibility: private
# ... other fields ...

secrets:
  org:
    - "11111111-1111-1111-1111-111111111111 > DATADOG_API_KEY"
  repo:
    - "33333333-3333-3333-3333-333333333333 > DATABASE_URL"
```

!!! note
    The Bitwarden secret UUID is the unique identifier shown in the Bitwarden Secrets Manager console.
    Org-level secrets are visible to all private repositories in the organisation by default.
    Repo-level secrets are scoped exclusively to the target repository.

## Scheduled Secret Rotation

The **`reusable-bitwarden-secret-rotation.yml`** workflow bulk-syncs every secret declared across all `repos/*.yml` files. It is called automatically by the daily cron pipeline (`CI - Cron`, runs at 06:32 UTC) so that any value updated in the Bitwarden vault is propagated to GitHub within 24 hours.

The rotation workflow can also be triggered manually via `workflow_dispatch` on the cron workflow for on-demand rotation.

### How the rotation works

1. Checks out the `.github` repository.
2. Scans every `repos/*.yml` file (excluding `_template.yml`) for a `secrets` block.
3. For each declared secret, calls `bws secret get <uuid>` to fetch the current value from Bitwarden.
4. Writes the value to GitHub using `gh secret set` at org or repo scope.
5. Prints a summary of secrets synced and any failures.

!!! warning
    The rotation workflow writes every declared secret on every run regardless of whether the value has changed in Bitwarden. This is intentional — it ensures secrets remain in sync even if a GitHub secret is accidentally deleted or overwritten.
