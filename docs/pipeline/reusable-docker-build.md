---
hide:
  - toc
---

# Reusable - Docker Build and Push

## What

This reusable workflow builds Docker images using [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/) and optionally pushes them to one or more container registries (GitHub Container Registry by default). It handles multi-platform builds, layer caching, image metadata, PR comments, and build provenance attestation.

## Why

Building and publishing container images is a repetitive task with many moving parts: registry authentication, cache management, tagging strategies, and PR feedback. Centralising this logic in a single reusable workflow ensures every repository follows the same tagging conventions (e.g. `latest`, `pr-<N>`, semver) and security practices (SBOM, provenance) without duplicating boilerplate in every pipeline.

## How

Call this workflow from any repository that produces a Docker image.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `attest-enable` | Create a build-provenance attestation | No | `false` |
| `build-args` | Docker `--build-arg` values | No | `""` |
| `comment-enable` | Post image tags as a PR comment | No | `true` |
| `context` | Docker build context path | No | `""` |
| `file` | Dockerfile path relative to context | No | `""` |
| `flavor-rules` | Flavor rules for docker-metadata-action | No | `latest=auto` |
| `ghcr-enable` | Log into GHCR | No | `true` |
| `image-names` | Registry/repository names to push to | No | `ghcr.io/${{ github.repository }}` |
| `platforms` | Platforms to build (comma-separated) | No | `linux/amd64` |
| `push` | Push image to registry after build | No | `true` |
| `tag-rules` | Tag rules for docker-metadata-action | No | See workflow defaults |
| `target` | Dockerfile build stage to target | No | `""` |

### Outputs

| Output | Description |
|---|---|
| `image-tag` | The primary image tag produced by this run |

### Secrets

None required beyond the built-in `GITHUB_TOKEN` (used automatically for GHCR login).

### Required Permissions

```yaml
permissions:
  contents: read
  packages: write
  pull-requests: write
```

### Example

```yaml
jobs:
  docker:
    name: Docker Build and Push
    uses: irishlab-io/.github/.github/workflows/reusable-docker-build.yml@main
    with:
      context: "."
      file: "Dockerfile"
      platforms: "linux/amd64,linux/arm64"
      push: true
    permissions:
      contents: read
      packages: write
      pull-requests: write
```
