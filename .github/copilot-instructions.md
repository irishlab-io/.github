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

# Run a single hook (e.g. yamllint, markdownlint)
pre-commit run yamllint --all-files
pre-commit run markdownlint --all-files

# Update pre-commit hook versions
pre-commit autoupdate
```

## Architecture

### Repository Lifecycle (GitOps)

1. A contributor opens a **[Repo Request] issue** using the issue form (`.github/ISSUE_TEMPLATE/repo-request.yml`)
2. `reusable-issue-to-repo.yml` auto-parses the form and opens a PR adding `repos/<name>.yml`
3. When the PR merges to `main`, `repo.yml` CI detects changed/deleted `repos/*.yml` files and calls `reusable-repo-creation.yml` or `reusable-repo-deletion.yml`
4. Creation fires a `repository-created` dispatch event, which triggers `reusable-repo-onboarding.yml` to apply rulesets, labels, Dependabot config, and Bitwarden secrets

### CI Entry Points

| File | Triggers |
|------|----------|
| `branch.yml` | Push to `dev`, `feat/*`, `fix/*`, `rel/*` |
| `pr.yml` | PRs targeting `main` |
| `main.yml` | Push to `main` |
| `cron.yml` | Daily schedule + manual dispatch |
| `repo.yml` | Push to `main` changing `repos/*.yml` |

All entry-point workflows delegate exclusively to `reusable-*.yml` via `workflow_call`.

### Reusable Workflows

All reusable workflows live in `.github/workflows/reusable-*.yml` and are referenced by other org repos as:

```yaml
uses: irishlab-io/.github/.github/workflows/reusable-<name>.yml@main
```

### Bot Authentication

Workflows that call the GitHub API use a GitHub App instead of `GITHUB_TOKEN`. Required secrets: `IRISHLAB_BOT_APP_ID` and `IRISHLAB_BOT_PRIVATE_KEY`. Standard token generation step:

```yaml
- uses: actions/create-github-app-token@<sha> # vX.Y.Z
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

First-party `irishlab-io/*` Actions are exempt. Enforced by the `pin-github-action` pre-commit hook (runs as a `manual` stage; `cron.yml` runs it on a daily schedule).

### YAML Lint Rules

Configured in `.config/.yaml-lint.yml`. Key constraints:
- Truthy values must be literal `true` or `false` — not `yes`/`no`/`on`/`off`
- Line length is disabled
- Workflow `on:` keys require `# yamllint disable-line rule:truthy` (reserved word conflict)

### New Repository Config (`repos/*.yml`)

Copy `repos/_template.yml` when adding a new repository. The `name` field **must match the filename** (without `.yml`). Naming convention requires a `svc-|lib-|infra-|sandbox-` prefix. The `git_workflow` field (`github-flow`, `gitflow`, `trunk`, `release-branch`) drives which ruleset profile is applied during onboarding.

### Rulesets

`rulesets/main.json` (branch protection) and `rulesets/tag.json` (tag protection) are synced to every active, non-template org repo by `reusable-org-sync.yml`. The `.github` repo itself is skipped during sync.

### Secrets via Bitwarden

Secrets are provisioned from Bitwarden Secrets Manager — not set directly. Format in `repos/*.yml`:

```yaml
secrets:
  repo:
    - "<bitwarden-uuid> > GITHUB_SECRET_NAME"
  org:
    - "<bitwarden-uuid> > ORG_SECRET_NAME"
```

### Commit Messages

[Conventional Commits](https://www.conventionalcommits.org/) enforced by the `commitizen` pre-commit hook on the `commit-msg` stage. Summary line ≤ 72 characters, imperative mood. Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `revert`.

### Copilot Instruction Files (scoped)

File-type-specific instructions live in `.github/instructions/` with `applyTo` frontmatter — they complement this file:

- `git-workflow.instructions.md` — applies to `**`
- `python-webapp.instructions.md` — applies to `**/*.py`
- `docker.instructions.md` — applies to `Dockerfile`, `docker-compose*.yml`
