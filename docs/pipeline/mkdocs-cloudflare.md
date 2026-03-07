---
hide:
  - toc
---

# MkDocs to Cloudflare Pages Deployment

The `reusable-mkdocs-cloudflare.yml` workflow builds a [MkDocs](https://www.mkdocs.org/)
documentation site and deploys it to [Cloudflare Pages](https://pages.cloudflare.com/).

## Prerequisites

Before using this workflow the following prerequisites must be in place.

### Cloudflare Prerequisites

1. **Cloudflare Account** – A Cloudflare account with Pages enabled.

2. **Cloudflare Pages Project** – A Pages project must already exist in your Cloudflare
   account. Create one via the Cloudflare Dashboard or with Wrangler:

   ```bash
   npx wrangler pages project create <project-name>
   ```

3. **Cloudflare API Token** – Create a token with the **Cloudflare Pages: Edit** permission:

   - Go to <https://dash.cloudflare.com/profile/api-tokens>
   - Click **Create Token** → **Use template** → **Edit Cloudflare Workers**
   - Under *Permissions*, add **Account > Cloudflare Pages > Edit**
   - Restrict the token to the target account and save it.

4. **Cloudflare Account ID** – Found on the Cloudflare Dashboard overview page for your
   domain, in the right-hand panel under **API** > **Account ID**.

### Repository Prerequisites

1. **MkDocs configuration** – A valid `mkdocs.yml` at the root (or in a subdirectory
   specified via `working-directory`) of the calling repository.

2. **UV lock file** – A `uv.lock` file with MkDocs and any required plugins listed as
   dev dependencies in `pyproject.toml`, for example:

   ```toml
   [dependency-groups]
   dev = [
       "mkdocs>=1.6.1",
       "mkdocs-material>=9.7.4",
   ]
   ```

3. **GitHub Secrets** – Add the following repository (or environment) secrets:

   | Secret name               | Description                                               |
   |---------------------------|-----------------------------------------------------------|
   | `CLOUDFLARE_API_TOKEN`    | Cloudflare API token with Pages edit permission           |
   | `CLOUDFLARE_ACCOUNT_ID`   | Your Cloudflare account ID                                |

## Usage

Reference the workflow from any repository within the organization:

```yaml
jobs:
  docs:
    name: Deploy Documentation
    uses: irishlab-io/.github/.github/workflows/reusable-mkdocs-cloudflare.yml@main
    with:
      cloudflare-project-name: my-docs-project
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

## Inputs

| Input                     | Required | Default       | Description                                                        |
|---------------------------|----------|---------------|--------------------------------------------------------------------|
| `cloudflare-project-name` | Yes      | —             | Cloudflare Pages project name to deploy to                         |
| `environment`             | No       | `production`  | GitHub deployment environment name                                 |
| `mkdocs-site-dir`         | No       | `site`        | MkDocs output directory (must match `site_dir` in `mkdocs.yml`)   |
| `python-version`          | No       | `3.14`        | Python version to use                                              |
| `uv-version`              | No       | `latest`      | UV version to use                                                  |
| `working-directory`       | No       | `.`           | Directory containing `mkdocs.yml`                                  |

## Secrets

| Secret                    | Required | Description                                              |
|---------------------------|----------|----------------------------------------------------------|
| `CLOUDFLARE_API_TOKEN`    | Yes      | Cloudflare API token with Pages edit permission          |
| `CLOUDFLARE_ACCOUNT_ID`   | Yes      | Your Cloudflare account ID                               |

## Full Example

```yaml
---
name: CI - Main

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy-docs:
    name: Deploy MkDocs to Cloudflare Pages
    uses: irishlab-io/.github/.github/workflows/reusable-mkdocs-cloudflare.yml@main
    with:
      cloudflare-project-name: my-org-docs
      python-version: "3.14"
      mkdocs-site-dir: site
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```
