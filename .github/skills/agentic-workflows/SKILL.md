---
name: agentic-workflows
description: Design, create, update, debug, or upgrade GitHub Agentic Workflows (gh-aw) in this repository.
---

# Agentic Workflows

Use this skill when a user asks to design, create, update, debug, or upgrade GitHub Agentic
Workflows in this repository. Agentic workflow **sources** are `.github/workflows/agentic-*.md` (natural-language frontmatter +
prompt) and are compiled by the `gh aw` CLI to `.github/workflows/agentic-*.lock.yml`. The
`.github/aw/` directory holds shared components and the `actions-lock.json` pin file.

> Naming convention: `reusable-*` is reserved for reusable workflows; agentic workflows use the
> `agentic-*` prefix so the two are never confused.

## This repo's workflows

The following agentic workflows are defined in `.github/workflows/` — read the one you're changing:

- `agentic-triage.md` — labels and summarizes new issues and PRs against `.github/labels.yml`.
- `agentic-repo-governance.md` — scheduled audit of org repos for ruleset/label/config drift.
- `agentic-docs-sync.md` — flags stale README/docs references when workflows or config change.
- `agentic-dep-review.md` — summarizes and security-reviews Dependabot/Renovate PRs.

Conventions for every workflow here:

- Least-privilege `permissions:`; the agent never writes directly — use **safe-outputs**
  (`add-labels`, `add-comment`, `create-pull-request`) so writes go through the compiled guard job.
- Actions and the firewall proxy are pinned via `.github/aw/actions-lock.json`; run
  `gh aw compile` after editing and commit the regenerated `.lock.yml`.
- Use the org GitHub App token (`IRISHLAB_BOT_APP_ID` / `IRISHLAB_BOT_PRIVATE_KEY`) for any
  cross-repo API access, per `.github/copilot-instructions.md`.

## Reference (upstream)

The full `gh-aw` prompt/reference library (syntax, safe-outputs, patterns, triggers,
token-optimization, MCP, subagents, etc.) is **not vendored here**. When you need it, fetch the
relevant file from the upstream `github/gh-aw` repository (e.g. via `gh` or WebFetch), for example
`https://raw.githubusercontent.com/github/gh-aw/main/.github/aw/<name>.md`. Load only the file you
need, then follow it directly. Start points:

- Create a workflow: `create-agentic-workflow.md`
- Update an existing one: `update-agentic-workflow.md`
- Debug / audit: `debug-agentic-workflow.md`
- Upgrade / fix deprecations: `upgrade-agentic-workflows.md`
- Safe outputs: `safe-outputs.md` · Syntax: `syntax.md` · Patterns: `patterns.md`
