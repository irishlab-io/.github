---
hide:
  - toc
---

# Reusable - Hello World

## What

This reusable workflow is a minimal test harness designed to validate that the shared workflow infrastructure (inputs, secrets, and composite actions) is wired up correctly. It runs a simple "Hello, world!" script and optionally exercises the [Tailscale composite action](../actions/tailscale.md) to verify VPN connectivity in CI.

## Why

When setting up or troubleshooting reusable workflows and composite actions, having a fast, low-risk workflow to call is invaluable. It lets you verify that secrets are properly passed through the `workflow_call` boundary, that boolean inputs control step execution correctly, and that the Tailscale network action connects successfully — all without running real workloads.

!!! warning
    This workflow is intended for **testing and validation purposes only**. Do not use it in production pipelines.

## How

Call this workflow during infrastructure validation or onboarding to confirm the CI setup is functioning end-to-end.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `comments` | A string printed to the log when `enable` is `true` | No | `test1234` |
| `enable` | Enables the optional echo and Tailscale steps | No | `false` |

### Secrets

| Secret | Description | Required |
|---|---|---|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID | Yes |
| `TS_OAUTH_CLIENT_SECRET` | Tailscale OAuth client secret | Yes |

### Example

```yaml
jobs:
  hello:
    name: Hello World Test
    uses: irishlab-io/.github/.github/workflows/reusable-hello-world.yml@main
    with:
      enable: true
      comments: "CI is working!"
    secrets:
      TS_OAUTH_CLIENT_ID: ${{ secrets.TS_OAUTH_CLIENT_ID }}
      TS_OAUTH_CLIENT_SECRET: ${{ secrets.TS_OAUTH_CLIENT_SECRET }}
```
