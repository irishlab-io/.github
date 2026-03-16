# Hugo Deploy to GitHub Pages

The `reusable-hugo-ghpages` workflow builds a [Hugo](https://gohugo.io/)
static site and deploys it to [GitHub Pages](https://pages.github.com/)
using the official GitHub Pages Actions.

## Prerequisites

Before calling this reusable workflow you must complete the following
one-time setup steps in the **target repository** (the one that contains
your Hugo site).

### 1. Enable GitHub Pages

1. Navigate to **Settings → Pages** in your repository.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Save the settings.

> Do **not** select a branch as the source — the workflow handles
> publishing automatically.

### 2. Configure Repository Permissions

The workflow requires two additional permissions on the calling workflow:

| Permission        | Reason                                                        |
| ----------------- | ------------------------------------------------------------- |
| `pages: write`    | Allows the workflow to publish the built site to GitHub Pages |
| `id-token: write` | Allows OIDC token creation for trusted Pages deployments      |

These must be declared in the **caller** workflow (either at top-level
`permissions:` or on the specific job that calls this reusable workflow).
If they are missing, GitHub fails with:
`The workflow is requesting 'pages: write', 'id-token: write', but is only allowed ...`.

### 3. Hugo Theme (optional)

If your Hugo site uses a theme managed as a **git submodule**, ensure
that the submodule is committed to your repository:

```bash
git submodule add https://github.com/<org>/<theme-repo> themes/<theme-name>
git commit -m "feat: add Hugo theme as submodule"
```

The workflow checks out submodules by default (`submodules: "true"`).
Set the input to `"recursive"` if you have nested submodules, or
`"false"` if you manage your theme another way (e.g., Hugo modules).

### 4. Repository Structure

Your repository must contain a valid Hugo site at the root level (or
adjust your `hugo-args` accordingly). The standard layout looks like:

```text
.
├── archetypes/
├── content/
├── layouts/
├── static/
├── themes/          # optional, git submodule
├── hugo.toml        # or config.toml / config.yaml
└── .github/
    └── workflows/
        └── deploy.yml
```

## Usage

Create a workflow file in your Hugo repository
(e.g. `.github/workflows/deploy.yml`):

```yaml
---
name: Deploy Hugo site to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main
```

If you prefer not to grant these permissions workflow-wide, set them on
the calling job instead:

```yaml
jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    permissions:
      contents: read
      pages: write
      id-token: write
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main
```

## Inputs

| Input           | Description                                           | Required | Default    |
| --------------- | ----------------------------------------------------- | -------- | ---------- |
| `hugo-version`  | Hugo version to install, e.g. `0.147.0` or `latest`   | No       | `latest`   |
| `hugo-extended` | Use Hugo extended (required for SCSS/SASS processing) | No       | `true`     |
| `publish-dir`   | Directory where Hugo outputs the built site           | No       | `./public` |
| `hugo-args`     | Additional arguments passed to the `hugo` build       | No       | `--minify` |
| `submodules`    | Submodule strategy: `true`, `false`, or `recursive`   | No       | `true`     |

## Outputs

| Output     | Description                                     |
| ---------- | ----------------------------------------------- |
| `page-url` | The URL of the deployed GitHub Pages site       |

## Advanced Usage

### Pin a specific Hugo version

```yaml
jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main
    with:
      hugo-version: "0.147.0"
```

### Pass extra build arguments

```yaml
jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main
    with:
      hugo-args: "--minify --environment production"
```

### Use recursive submodules

```yaml
jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main
    with:
      submodules: "recursive"
```

### Use the deployed URL downstream

```yaml
jobs:
  hugo-deploy:
    name: Build and Deploy Hugo Site
    uses: irishlab-io/.github/.github/workflows/reusable-hugo-ghpages.yml@main

  notify:
    name: Print deployed URL
    needs: hugo-deploy
    runs-on: ubuntu-24.04
    steps:
      - name: Show deployed URL
        run: echo "Site is live at ${{ needs.hugo-deploy.outputs.page-url }}"
        shell: bash
```

## How It Works

The workflow is split into two jobs to satisfy GitHub Pages' OIDC
deployment requirements:

```mermaid
flowchart LR
  checkout[Checkout repository] --> setup[Setup Hugo]
  setup --> configure[Configure Pages]
  configure --> build[hugo build]
  build --> upload[Upload Pages artifact]
  upload --> deploy[Deploy to GitHub Pages]
```

1. **build** — checks out the repository (including submodules), installs
   Hugo, configures the Pages base URL, builds the site, and uploads the
   resulting `public/` directory as a Pages artifact.
2. **deploy** — runs under the `github-pages` environment and calls the
   official `actions/deploy-pages` action to publish the artifact.
