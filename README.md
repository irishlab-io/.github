# irishlab-io/.github

The organization's **special repository**. It provides governance, reusable CI/CD, curated AI
tooling, and agentic workflows shared across every repo in the `irishlab-io` organization.

> Status: work in progress — parts of the GitOps repo-management pipeline are still being built.
> Sections marked _planned_ are not yet implemented.

## What's here

| Path | Purpose |
|------|---------|
| `.github/workflows/reusable-*.yml` | Reusable CI/CD workflows consumed by org repos |
| `.github/workflows/{branch,pr,main,cron,repo}.yml` | This repo's own CI entry points |
| `.github/rulesets/` | Branch (`main.json`) and tag (`tag.json`) protection templates |
| `.github/labels.yml` | Standard org labels synced to repos |
| `.github/agents`, `.github/instructions`, `.github/skills` | Curated AI tooling — see [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| `.github/workflows/aw-*.md` | Agentic workflows (`gh-aw`) — automated triage, governance, docs, deps |
| `.github/aw/` | The `gh-aw` action pin lockfile (`actions-lock.json`) |
| `repos/` | GitOps repository definitions (`repos/<name>.yml`) _(planned pipeline)_ |
| `profile/README.md` | Public org profile shown on github.com/irishlab-io |
| `docs/` | Long-form reference documentation |

## Consuming a reusable workflow

From any repo in the org, call a reusable workflow by path and ref:

```yaml
jobs:
  lint:
    uses: irishlab-io/.github/.github/workflows/reusable-prek.yml@main
    with:
      required: true          # fail the job on findings (default); set false for advisory-only
```

Available reusable workflows include: `reusable-prek`, `reusable-gitguardian`, `reusable-sast`,
`reusable-sca`, `reusable-secret`, `reusable-python-uv`, `reusable-docker-build`,
`reusable-terraform-plan` / `reusable-terraform-apply`, `reusable-renovate`,
`reusable-dependabot-auto`, `reusable-gh-labeler`, `reusable-gh-pin-actions`, and more — see
`.github/workflows/`.

## Branching model

A minor variation of Gitflow:

| Branch | Purpose |
|--------|---------|
| `main` | Latest production codebase |
| `dev` | Aggregates features and development |
| `feat/*` | New features |
| `rel/*` | Release preparation |
| `fix/*` | Hotfixes to production |
| `renovate/*` | Dependency updates ([Renovate](https://www.mend.io/renovate/)) |

## Conventions

- **Conventional Commits**, enforced by commitizen (`commit-msg` hook).
- **SHA-pinned Actions** with a version comment; enforced by `pin-github-action`.
- Pre-commit gate: `pre-commit run --all-files` (commitizen, ggshield, markdownlint, yamllint,
  actionlint).

## AI tooling

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for the curated agents,
instructions, and skills, and `.github/workflows/aw-*.md` for the agentic workflows that run in CI.
