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

## GitHub App setup

Create one organisation-owned GitHub App and install it on every repository that should use the workflow.

### 1. Register the app

In GitHub:

1. Go to your organisation settings
2. Open Developer settings
3. Select GitHub Apps
4. Create a new app

Suggested values:

| Setting | Value |
|---|---|
| App name | `irishlab-bot` or similar |
| Homepage URL | Your organisation URL or repository URL |
| Webhook | Disable for this use case |

### 2. Grant the minimum repository permissions

This workflow creates, updates, lists, and deletes repository labels. The app therefore needs:

| Permission type | Permission | Access |
|---|---|---|
| Repository | Issues | Read and write |

Notes:

- `Metadata` read access is provided automatically by GitHub Apps
- No organisation permissions are required for this workflow
- If you later add more permissions, GitHub will require the installation to approve them before they take effect

### 3. Install the app

Install the app on:

- all repositories in the organisation, or
- only the repositories that will run label synchronisation

If the app is not installed on a target repository, token generation succeeds only for repositories included in the installation scope.

### 4. Generate and store the private key

After creating the app:

1. Open the app settings page
2. Generate a private key
3. Download the `.pem` file

Store the values as organisation secrets:

| Secret | Value |
|---|---|
| `IRISHLAB_BOT_APP_ID` | The numeric GitHub App ID |
| `IRISHLAB_BOT_PRIVATE_KEY` | Full contents of the downloaded `.pem` file |

Recommended scope:

- store both secrets at the organisation level
- restrict access to the repositories that will call the reusable workflow

### 5. Call the workflow

The caller must pass the secrets to the reusable workflow:

```yaml
jobs:
  sync-labels:
    uses: irishlab-io/.github/.github/workflows/reusable-sync-label.yml@main
    secrets: inherit
```

### 6. Validate the setup

Run the workflow manually once and confirm that:

- the `Generate Token` step succeeds
- the `Sync Labels` step reads `.github/labels.yml`
- labels are created or updated in the target repository

Typical failures:

| Symptom | Likely cause |
|---|---|
| `Resource not accessible by integration` | App is missing `Issues: Read and write` or the installation has not approved the permission |
| Token generation fails | Wrong `IRISHLAB_BOT_APP_ID`, invalid private key, or app not installed on the repository owner |
| Workflow cannot read secrets | Caller forgot `secrets: inherit` or the secrets are not shared with that repository |

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
