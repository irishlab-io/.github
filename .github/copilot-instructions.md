# Copilot Instructions

## Repository Purpose

This is the `irishlab-io/.github` special repository. It manages organization-wide GitHub governance:

- **Reusable workflows** consumed by every org repo via `irishlab-io/.github/.github/workflows/reusable-*.yml@main`
- **GitOps repo management** _(planned)_ — adding/modifying `repos/<name>.yml` triggers automated repository creation, configuration, and secret provisioning
- **Org-wide standards** — rulesets (`.github/rulesets/*.json`), labels (`.github/labels.yml`), Renovate config, and Dependabot templates synced to all repos
- **Curated AI tooling** — agents, instructions, skills, and agentic workflows under `.github/` (see [AI Tooling Assets](#ai-tooling-assets))

## Commands

```bash
# Run all pre-commit hooks
pre-commit run --all-files --color auto

# Run a single hook (e.g. yamllint, markdownlint)
pre-commit run yamllint --all-files
pre-commit run markdownlint --all-files

# Update pre-commit hook versions
pre-commit autoupdate

# Compile agentic workflows after editing .github/workflows/aw-*.md
gh aw compile
```

## Architecture

### Repository Lifecycle (GitOps) — _planned_

The following pipeline is the intended design; the `reusable-*` workflows named here are **not yet implemented**. Do not reference them from CI until they exist.

1. A contributor opens a **[Repo Request] issue** using the issue form (`.github/ISSUE_TEMPLATE/repo-request.yml`)
2. `reusable-issue-to-repo.yml` auto-parses the form and opens a PR adding `repos/<name>.yml`
3. When the PR merges to `main`, `repo.yml` CI detects changed/deleted `repos/*.yml` files and calls `reusable-repo-creation.yml` or `reusable-repo-deletion.yml`
4. Creation fires a `repository-created` dispatch event, which triggers `reusable-repo-onboarding.yml` to apply rulesets, labels, Dependabot config, and Bitwarden secrets

### Policy Fan-Out (OrchestratorOps)

Org policies are authored as `docs/policy/*.md` (frontmatter `id`, `title`, `status`) and turned into per-repository work by a two-layer [OrchestratorOps](https://github.github.com/gh-aw/patterns/orchestrator-ops/) pair:

1. `aw-policy-orchestrator.md` fires on a push to `main` touching `docs/policy/**.md`. It reads `.github/policy-targets.yml`, opens one tracking issue here, and dispatches one worker run per target with a shared `tracker_id`.
2. `aw-policy-worker.md` handles exactly one repo per run and files at most one `[policy]` issue in it. It is read-only against the target — never a push or PR.

Both import `.github/agents/architect.md`, which owns the policy → activities reasoning.

Two constraints drive this shape, and are worth knowing before changing it:

- `dispatch-workflow`/`call-workflow` are **same-repo only**. Cross-repo reach comes from `create-issue` with `target-repo`/`allowed-repos`, so the worker runs here and writes outward.
- `allowed-repos` is **static frontmatter** evaluated at compile time — it cannot be derived from `.github/policy-targets.yml` at runtime. That file is data for the agent; `allowed-repos` is the enforced boundary. The worker's `github-app.repositories` scope must list the same repos plus `.github` (needed to read the policy), or cross-repo writes fail.

### CI Entry Points

| File | Triggers |
|------|----------|
| `branch.yml` | Push to `dev`, `feat/*`, `fix/*`, `rel/*` |
| `pr.yml`     | PRs targeting `main` |
| `main.yml`   | Push to `main` |
| `cron.yml`   | Daily schedule + manual dispatch |
| `repo.yml`   | Push to `main` changing `repos/*.yml` |

All entry-point workflows delegate exclusively to `reusable-*.yml` via `workflow_call`.

### Reusable Workflows

Reusable workflows **must** be named `reusable-*.yml` — the prefix is reserved for them so they are never confused with this repo's CI entry points or the `aw-*` (`gh-aw`) workflows. They live in `.github/workflows/reusable-*.yml` and are referenced by other org repos as:

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

## AI Tooling Assets

Everything an AI coding agent needs to work in this org lives under `.github/`, so it is discoverable from a single, GitHub-native location and shared to consuming repos.

| Directory | What it holds |
|-----------|---------------|
| `.github/agents/` | Agent personas — role definitions to adopt for a task |
| `.github/instructions/` | Scoped coding standards (`*.instructions.md`, `applyTo` frontmatter) |
| `.github/skills/` | Skills — task procedures an agent invokes on demand |
| `.github/workflows/aw-*.md` | Agentic workflows (`gh-aw`) that run in CI |

### Agents (`.github/agents/`)

| Agent | Use for |
|-------|---------|
| `architect` | Turning `docs/policy/*.md` into concrete per-repo activities |
| `code-reviewer` | General code review |
| `coding-agent` | Implementing features/fixes end-to-end |
| `security-analyst` | Security review and threat analysis |
| `technical-writer` | Docs, READMEs, changelogs |
| `terraform-reviewer` | Reviewing Terraform / IaC |
| `test-engineer` | Writing and improving tests |

### Skills (`.github/skills/`)

Invoke a skill when its task matches. Highlights:

- **Governance / AI**: `agentic-workflows`, `resolve-issue-pr`, `security-remediation`
- **Git & GitHub**: `git-commit`, `git-flow-branch-creator`, `gh-cli`, `github-issues`
- **Python**: `pytest-coverage`, `ruff-recursive-fix`, `python-mcp-server-generator`
- **Refactoring**: `refactor`, `refactor-plan`, `refactor-method-complexity-reduce`, `review-and-refactor`
- **Docker / supply chain**: `multi-stage-dockerfile`, `dependabot`, `dependency-track`, `gitguardian`
- **Docs / misc**: `readme-blueprint-generator`, `repo-story-time`, `meeting-minutes`, `github-copilot-starter`

Each skill is a `SKILL.md` (name + description frontmatter) with optional `references/` and `scripts/`. See a skill's own file for its procedure.

### Asset Conventions

- These assets are **org-neutral**: they describe *how* to work, not any single downstream app. Repo-specific grounding belongs in that repo's own instructions file.
- Skills must not contain secrets, credentials, or references to private/other-org repositories.

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

`.github/rulesets/main.json` (branch protection) and `.github/rulesets/tag.json` (tag protection) are the org templates, applied to every active, non-template org repo during onboarding. The `.github` repo itself is skipped. (The `reusable-org-sync.yml` workflow that automates this is _planned_.)

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

File-type-specific instructions live in `.github/instructions/` with `applyTo` frontmatter — they complement this file. For example:

- `git-workflow.instructions.md` — git branching/commit workflow
- `best-practices-python.instructions.md` — applies to `**/*.py`
- `best-practices-docker.instructions.md` — applies to `Dockerfile`, `docker-compose*.yml`
- `best-practices-github-actions.instructions.md` — applies to `.github/workflows/*.yml`

The full set: `git-workflow`, `makefile`, `tool-shell`, `assist-code-review`, `assist-markdown`, `assist-security`, and `best-practices-*` for Docker, GitHub Actions, JavaScript, and Python, plus the `guideline-JPL_Coding_Standard_C` reference.
