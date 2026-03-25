---
hide:
  - toc
---

# Reusable - Bitwarden Secret Deploy

## What

This reusable workflow fetches secrets from [Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/) and renders them into one of several target formats so that workloads can consume them directly.

| Format | Output |
|---|---|
| `env` | `.env`-style `KEY=VALUE` file (dotenv) |
| `json` | JSON object `{"KEY": "value"}` |
| `yaml` | YAML mapping `KEY: value` |
| `k8s-secret` | Kubernetes `Secret` manifest (values base64-encoded) |
| `k8s-configmap` | Kubernetes `ConfigMap` manifest (plain-text values) |
| `raw` | Single raw secret value written to a plain-text file |

The rendered file is uploaded as a GitHub Actions artifact (1-day retention by default). When the format is `k8s-secret` or `k8s-configmap` and `k8s_apply: true`, the manifest is also applied to the cluster via `kubectl apply`.

## Why

Different workloads consume secrets in different ways. This workflow removes per-project boilerplate by providing a single, reusable entry point that adapts its output to the consumer's expected format.

## How

### Prerequisites

| Secret | Description |
|---|---|
| `BW_ACCESS_TOKEN` | Bitwarden Secrets Manager machine account access token |
| `KUBECONFIG` | Base64-encoded kubeconfig — only required when `k8s_apply: true` |

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `secrets` | Newline-separated `<bitwarden-uuid> > VARIABLE_NAME` mappings | Yes | — |
| `format` | Output format (`env`, `json`, `yaml`, `k8s-secret`, `k8s-configmap`, `raw`) | Yes | — |
| `output_file` | Filename for the rendered artifact (no path). Auto-set based on format if omitted. | No | format-based default |
| `artifact_name` | Name of the GitHub Actions artifact to upload | No | `bitwarden-secret-deploy` |
| `artifact_retention_days` | Days to retain the artifact | No | `1` |
| `k8s_name` | Kubernetes resource name (`k8s-secret` / `k8s-configmap` only) | No | `app-secrets` |
| `k8s_namespace` | Kubernetes namespace (`k8s-secret` / `k8s-configmap` only) | No | `default` |
| `k8s_apply` | Apply the rendered k8s manifest to the cluster via `kubectl apply` | No | `false` |

### Outputs

| Output | Description |
|---|---|
| `artifact_name` | Name of the uploaded artifact |
| `output_file` | Filename of the rendered secrets file within the artifact |

### Example — generate a dotenv file

```yaml
jobs:
  deploy-env:
    name: Deploy secrets as .env
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret-deploy.yml@main
    with:
      format: env
      secrets: |
        11111111-1111-1111-1111-111111111111 > DATABASE_URL
        22222222-2222-2222-2222-222222222222 > REDIS_URL
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
```

### Example — generate a JSON config file

```yaml
jobs:
  deploy-json:
    name: Deploy secrets as JSON
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret-deploy.yml@main
    with:
      format: json
      output_file: config.json
      secrets: |
        33333333-3333-3333-3333-333333333333 > API_KEY
        44444444-4444-4444-4444-444444444444 > API_SECRET
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
```

### Example — render and apply a Kubernetes Secret

```yaml
jobs:
  deploy-k8s-secret:
    name: Deploy secrets to Kubernetes
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret-deploy.yml@main
    with:
      format: k8s-secret
      k8s_name: payments-api-secrets
      k8s_namespace: production
      k8s_apply: true
      secrets: |
        55555555-5555-5555-5555-555555555555 > DATABASE_URL
        66666666-6666-6666-6666-666666666666 > STRIPE_SECRET_KEY
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
      KUBECONFIG: ${{ secrets.KUBECONFIG }}
```

### Example — render a Kubernetes ConfigMap

```yaml
jobs:
  deploy-k8s-configmap:
    name: Deploy config to Kubernetes
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret-deploy.yml@main
    with:
      format: k8s-configmap
      k8s_name: payments-api-config
      k8s_namespace: production
      k8s_apply: true
      secrets: |
        77777777-7777-7777-7777-777777777777 > LOG_LEVEL
        88888888-8888-8888-8888-888888888888 > FEATURE_FLAGS
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
      KUBECONFIG: ${{ secrets.KUBECONFIG }}
```

### Example — write a single raw secret to a file

```yaml
jobs:
  deploy-raw:
    name: Export raw secret
    uses: irishlab-io/.github/.github/workflows/reusable-bitwarden-secret-deploy.yml@main
    with:
      format: raw
      output_file: tls.key
      secrets: |
        99999999-9999-9999-9999-999999999999 > TLS_PRIVATE_KEY
    secrets:
      BW_ACCESS_TOKEN: ${{ secrets.BW_ACCESS_TOKEN }}
```

### Downloading the artifact in a subsequent job

```yaml
  use-secrets:
    needs: deploy-env
    runs-on: ubuntu-24.04
    steps:
      - name: Download rendered secrets
        uses: actions/download-artifact@v4
        with:
          name: ${{ needs.deploy-env.outputs.artifact_name }}

      - name: Load env file
        run: |
          set -a
          source .env
          set +a
          # ... continue with secrets available as env vars
```

!!! warning
    Rendered secrets are uploaded as GitHub Actions artifacts. Artifacts are accessible to all users with read access to the repository. Use `artifact_retention_days: 1` (the default) and ensure repository access is appropriately restricted.
    For Kubernetes targets, the `k8s-secret` format base64-encodes values as required by the Kubernetes API. The `k8s-configmap` format stores values as plain text — only use it for non-sensitive configuration data.
