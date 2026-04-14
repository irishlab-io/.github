# Copilot Instructions

## Repository Purpose

This is the `irishlab-io/.github` special repository. It manages organization-wide GitHub governance:
- **Reusable workflows** consumed by every org repo via `irishlab-io/.github/.github/workflows/reusable-*.yml@main`
- **GitOps repo management** — adding/modifying `repos/<name>.yml` triggers automated repository creation, configuration, and secret provisioning
- **Org-wide standards** — rulesets (`rulesets/*.json`), labels (`.github/labels.yml`), Renovate config, and Dependabot templates synced to all repos
- **Documentation** served via MkDocs Material to Cloudflare Pages

## Commands

```bash
# Install dependencies
uv sync

# Serve docs locally
uv run mkdocs serve

# Build docs
uv run mkdocs build

# Run all pre-commit hooks
pre-commit run --all-files --color auto

# Run a single hook (e.g. yamllint, markdownlint, commitizen)
pre-commit run yamllint --all-files
pre-commit run markdownlint --all-files

# Update pre-commit hook versions
pre-commit autoupdate
```

## Architecture

### Repository Lifecycle (GitOps)

1. A contributor opens a **[Repo Request] issue** using the issue form (`.github/ISSUE_TEMPLATE/repo-request.yml`)
2. The `reusable-issue-to-repo.yml` workflow auto-parses the form and opens a PR adding `repos/<name>.yml`
3. When the PR merges to `main`, `repo.yml` CI detects changed/deleted `repos/*.yml` files and calls `reusable-repo-creation.yml` or `reusable-repo-deletion.yml`
4. Creation triggers a `repository-created` dispatch event, which kicks off `reusable-repo-onboarding.yml` to apply rulesets, labels, Dependabot config, and Bitwarden secrets

### CI Workflows (entry points)

| File | Triggers |
|------|----------|
| `branch.yml` | Push to `dev`, `feat/*`, `fix/*`, `rel/*` |
| `pr.yml` | PRs targeting `main` |
| `main.yml` | Push to `main` |
| `cron.yml` | Daily schedule + manual dispatch |
| `repo.yml` | Push to `main` changing `repos/*.yml` |

All entry-point workflows delegate to `reusable-*.yml` via `workflow_call`.

### Reusable Workflows

All reusable workflows live in `.github/workflows/reusable-*.yml` and are consumed by other org repos using:

```yaml
uses: irishlab-io/.github/.github/workflows/reusable-<name>.yml@main
```

### Authentication

Workflows that call the GitHub API use a GitHub App (not `GITHUB_TOKEN`). Secrets required:
- `IRISHLAB_BOT_APP_ID` — GitHub App ID
- `IRISHLAB_BOT_PRIVATE_KEY` — GitHub App private key

Token generation step pattern:
```yaml
- uses: actions/create-github-app-token@<sha>
  id: generate-token
  with:
    app-id: "${{ secrets.IRISHLAB_BOT_APP_ID }}"
    private-key: "${{ secrets.IRISHLAB_BOT_PRIVATE_KEY }}"
    owner: "${{ github.repository_owner }}"
```

## Key Conventions

### GitHub Actions SHA Pinning

All third-party Actions must be pinned to a full commit SHA with a version comment:
```yaml
uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
```
First-party `irishlab-io/*` Actions are exempt. This is enforced by the `pin-github-action` pre-commit hook (runs as `manual` stage; the `cron.yml` workflow runs it on schedule).

### YAML Lint Rules

Configured in `.config/.yaml-lint.yml`. Key constraints:
- Truthy values must be literal `true` or `false` (not `yes`/`no`/`on`/`off`)
- Line length is disabled
- Workflows use `# yamllint disable-line rule:truthy` on `on:` keys (reserved word conflict)

### New Repository Config (`repos/*.yml`)

Copy `repos/_template.yml` when adding a new repository. The `name` field **must match the filename** (without `.yml`). Naming convention: `svc-|lib-|infra-|sandbox-` prefix. The `git_workflow` field drives which ruleset profile is applied.

### Rulesets

`rulesets/main.json` and `rulesets/tag.json` define org-standard branch and tag protection rules. These are synced to every non-archived, non-template org repo by `reusable-org-sync.yml`. The `.github` repo itself is skipped during sync.

### Secrets (Bitwarden)

Secrets are provisioned from Bitwarden Secrets Manager, not set directly. Format in `repos/*.yml`:
```yaml
secrets:
  repo:
    - "<bitwarden-uuid> > GITHUB_SECRET_NAME"
```

### Copilot Instructions Files

Context-specific instructions live in `.github/instructions/` with `applyTo` frontmatter:
- `git-workflow.instructions.md` — applies to `**`
- `python-webapp.instructions.md` — applies to `**/*.py`
- `docker.instructions.md` — applies to Dockerfile/docker-compose files

### Commit Messages

[Conventional Commits](https://www.conventionalcommits.org/) enforced by `commitizen` pre-commit hook on `commit-msg` stage. Summary line ≤ 72 characters, imperative mood.
