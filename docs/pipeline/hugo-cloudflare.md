# Hugo - Cloudflare Pages Deploy

This document explains how to use the
[`reusable-hugo-cloudflare.yml`](../../.github/workflows/reusable-hugo-cloudflare.yml)
reusable workflow to automatically build a Hugo static site and deploy it to
[Cloudflare Pages](https://pages.cloudflare.com/).

---

## Overview

The workflow performs the following steps:

1. **Checkout** the repository (including Git submodules for themes)
2. **Install Hugo** (configurable version, extended edition by default)
3. **Cache** Hugo modules and built resources for faster subsequent runs
4. **Build** the Hugo site with minification and garbage collection enabled
5. **Deploy** the built site to Cloudflare Pages using the Wrangler CLI
6. **Register custom domain** (optional) — associate a custom hostname and
   auto-provision DNS if the zone is managed by Cloudflare

---

## Prerequisites

Before calling this workflow you must:

1. **Create a Cloudflare Pages project** in your Cloudflare dashboard.
   The project must exist before the first deployment — Wrangler will not
   create it automatically.
2. **Create the two GitHub secrets** described below in the repository
   (or organisation) that calls this workflow.

---

## Required GitHub Secrets

Both secrets are **required**. The workflow will fail if either is missing.

### `CLOUDFLARE_API_TOKEN`

A Cloudflare API token that grants the workflow permission to create and
update Pages deployments.

#### How to create the token

1. Log in to the [Cloudflare dashboard](https://dash.cloudflare.com/).
2. Navigate to **My Profile → API Tokens → Create Token**.
3. Select **Create Custom Token**.
4. Configure the token with the settings below.
5. Click **Continue to summary → Create Token**.
6. Copy the token immediately (it is shown only once).

| Setting | Value |
| --- | --- |
| **Token name** | `github-actions-pages` (or any descriptive name) |
| **Permissions** | `Account` → `Cloudflare Pages` → **Edit** |
| **Account Resources** | `Include` → *your account* |
| **IP Address Filtering** | Optional — restrict to GitHub Actions IP ranges |
| **TTL** | Optional — set an expiry date for token rotation |

> **Minimum required permission:** `Account: Cloudflare Pages: Edit`
> Do **not** grant Zone, DNS, Worker, or any other permissions —
> follow the principle of least privilege.

#### Add API Token Secret to GitHub

Navigate to **Repository Settings → Secrets and variables → Actions →
New repository secret** and set:

```text
Name:  CLOUDFLARE_API_TOKEN
Value: <paste the token>
```

Or at the organisation level for use across multiple repositories:

Navigate to **Organisation Settings → Secrets and variables → Actions →
New organisation secret** and set:

```text
Name:  CLOUDFLARE_API_TOKEN
Visibility: Selected repositories (choose only the repos that need it)
```

---

### `CLOUDFLARE_ACCOUNT_ID`

Your Cloudflare **Account ID** — a 32-character hexadecimal string that
identifies your Cloudflare account.

#### How to find your Account ID

1. Log in to the [Cloudflare dashboard](https://dash.cloudflare.com/).
2. Select any domain from your account, or navigate to **Workers & Pages**.
3. The Account ID is displayed in the right-hand sidebar under **API**.

Alternatively, retrieve it with the Cloudflare API:

```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer <your-api-token>" \
  -H "Content-Type: application/json" \
  | jq '.result[0].id'
```

#### Add Account ID Secret to GitHub

Navigate to **Repository Settings → Secrets and variables → Actions →
New repository secret** and set:

```text
Name:  CLOUDFLARE_ACCOUNT_ID
Value: <your 32-character account ID>
```

> **Note:** The Account ID is not a secret in the traditional sense (it
> appears in Cloudflare dashboard URLs), but storing it as a secret prevents
> it from being exposed in workflow logs.

---

## Usage

### Minimal caller workflow

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main

jobs:
  deploy:
    name: Deploy to Cloudflare Pages
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-cloudflare.yml@main
    with:
      cloudflare-project-name: my-blog
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

### Full example with all inputs

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

jobs:
  deploy-preview:
    name: Deploy Preview to Cloudflare Pages
    if: github.event_name == 'pull_request'
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-cloudflare.yml@main
    with:
      cloudflare-project-name: my-blog
      environment: staging
      hugo-version: "0.147.0"
      hugo-extended: true
      submodules: recursive
      working-directory: .
      publish-directory: public
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

  deploy-production:
    name: Deploy to Cloudflare Pages (Production)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-cloudflare.yml@main
    with:
      cloudflare-project-name: my-blog
      environment: production
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

---

## Inputs Reference

| Input | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `cloudflare-project-name` | `string` | **Yes** | — | Name of the Cloudflare Pages project |
| `custom-domain` | `string` | No | `""` | Custom domain to associate (e.g. `blog.example.com`) |
| `environment` | `string` | No | `production` | GitHub environment name |
| `hugo-extended` | `boolean` | No | `true` | Install the Hugo extended edition (SCSS/SASS) |
| `hugo-version` | `string` | No | `latest` | Hugo version to install (e.g. `0.147.0`) |
| `publish-directory` | `string` | No | `public` | Output directory written by Hugo |
| `submodules` | `string` | No | `recursive` | Git submodule checkout mode |
| `working-directory` | `string` | No | `.` | Path to the Hugo project root |

## Outputs Reference

| Output | Description |
| --- | --- |
| `deployment-url` | URL of the Cloudflare Pages deployment |

---

## Cloudflare Pages Project Setup

If you have not yet created a Cloudflare Pages project, follow these steps:

1. In the Cloudflare dashboard, go to
   **Workers & Pages → Create application → Pages**.
2. Choose **Direct Upload** (since this workflow uploads from the CLI).
3. Enter a **Project name** — this must match the `cloudflare-project-name`
   input exactly.
4. Click **Create project**.

For branch-based preview deployments, Cloudflare Pages automatically creates
a unique URL for every branch deployed.

---

## Custom Domain & DNS

The optional `custom-domain` input attaches a hostname to your Cloudflare
Pages project after each deployment. The workflow calls the
[Cloudflare Pages domains API](https://developers.cloudflare.com/api/resources/pages/subresources/domains/methods/add/)
and is idempotent — running it again when the domain is already registered
will not return an error.

### API Token permissions

No additional permissions are needed beyond the base requirement.
`Account: Cloudflare Pages: Edit` covers custom domain registration.

If you also want the workflow to manage DNS records for a zone that is
**not** on Cloudflare, you must handle that at your external DNS provider
(see below). For Cloudflare-managed zones, DNS is provisioned automatically.

### Domain on Cloudflare DNS (recommended)

When the zone for your custom domain is already in your Cloudflare account:

1. Set the `custom-domain` input to the hostname (e.g. `blog.example.com`).
2. The workflow registers the domain with the Pages project.
3. Cloudflare automatically creates a `CNAME` DNS record pointing to
   `<project>.pages.dev`.
4. A free TLS certificate is provisioned automatically — no extra steps.

```yaml
jobs:
  deploy:
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-cloudflare.yml@main
    with:
      cloudflare-project-name: my-blog
      custom-domain: blog.example.com
    secrets:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

### Domain on an External DNS Provider

When the zone is managed outside Cloudflare (e.g. Route 53, Namecheap):

1. Set the `custom-domain` input — the workflow registers the domain with
   the Pages project and requests a TLS certificate from Cloudflare.
2. Add the appropriate DNS record at your provider:

   - **Subdomain** (e.g. `blog.example.com`) — create a `CNAME` record:

     | Type | Host | Value |
     | --- | --- | --- |
     | `CNAME` | `blog` | `<project>.pages.dev` |

   - **Apex domain** (e.g. `example.com`) — `CNAME` is not valid at the zone
     apex. Use an `ALIAS` or `ANAME` record if your provider supports it, or
     delegate the zone to Cloudflare to benefit from CNAME flattening:

     | Type | Host | Value |
     | --- | --- | --- |
     | `ALIAS` / `ANAME` | `@` | `<project>.pages.dev` |

> **DNS propagation:** Changes can take up to 48 hours to propagate globally,
> though most providers resolve within minutes.

### Removing a custom domain

To detach a domain from the Pages project, call the Cloudflare API manually
or use the Cloudflare dashboard (**Pages → your project → Custom domains →
Remove**). Remove the corresponding DNS record at your provider afterwards.

---

## GitHub Environment Protection (Optional)

For production deployments, consider creating a
[GitHub Environment](https://docs.github.com/en/actions/deployment/targeting-different-deployment-environments/using-environments-for-deployment)
named `production` with:

- **Required reviewers** — manual approval gate before production deploys
- **Deployment branches** — restrict to the `main` branch only

This ensures that only approved, merged code reaches your production site.

---

## Security Considerations

- The `CLOUDFLARE_API_TOKEN` should be scoped to **Cloudflare Pages Edit**
  only. Never use a Global API Key.
- Rotate the API token periodically. Use the token's TTL setting to enforce
  rotation.
- Store both secrets at the repository or organisation level — never
  hard-code them in workflow files.
- The workflow requests only `contents: read` and `deployments: write`
  GitHub permissions.
