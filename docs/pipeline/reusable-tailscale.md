---
hide:
  - toc
---

# Reusable - Connect to Tailscale

## What

This reusable workflow connects a GitHub Actions runner to a [Tailscale](https://tailscale.com/) tailnet using OAuth credentials. Once connected, subsequent steps in the calling workflow can reach private resources (databases, internal APIs, self-hosted services) that are only accessible over the tailnet.

## Why

Many infrastructure resources — self-hosted SonarQube, internal artifact registries, private APIs — should never be exposed to the public internet. Tailscale provides a lightweight, zero-trust VPN that allows CI runners to reach these resources securely without firewall changes or static IP allowlisting. Encapsulating the connection logic in a single reusable workflow ensures that every pipeline connects consistently and that credentials are managed in one place.

## How

Call this workflow at the start of any job that needs access to private tailnet resources. Subsequent steps in the **calling** job will have network access to the tailnet for the duration of the job.

!!! note
    Because each `uses: workflow_call` job runs in its own isolated runner, you must call this workflow — or the equivalent [Tailscale composite action](./../actions/tailscale.md) — in every job that requires VPN access. Network state is not shared across jobs.

### Inputs

None.

### Secrets

| Secret | Description | Required |
|---|---|---|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID | Yes |
| `TS_OAUTH_CLIENT_SECRET` | Tailscale OAuth client secret | Yes |

### Prerequisites

- A Tailscale OAuth client with the `devices` scope
- A tag policy that allows the `tag:ci` tag (or adjust the tag inside the workflow)

### Example

```yaml
jobs:
  connect-vpn:
    name: Connect to Tailscale
    uses: irishlab-io/.github/.github/workflows/reusable-tailscale.yml@main
    secrets:
      TS_OAUTH_CLIENT_ID: ${{ secrets.TS_OAUTH_CLIENT_ID }}
      TS_OAUTH_CLIENT_SECRET: ${{ secrets.TS_OAUTH_CLIENT_SECRET }}
```
