# AGENTS.md

Curated AI tooling for the **irishlab-io** organization. Everything an AI coding agent needs to
work in this org lives under `.github/`, so it is discoverable from a single, GitHub-native
location and shared to consuming repos.

| Directory | What it holds |
|-----------|---------------|
| `.github/agents/` | Agent personas — role definitions to adopt for a task |
| `.github/instructions/` | Scoped coding standards (`*.instructions.md`, `applyTo` frontmatter) |
| `.github/skills/` | Skills — task procedures an agent invokes on demand |
| `.github/aw/` | Agentic workflows (`gh-aw`) that run in CI |
| `.github/copilot-instructions.md` | Repo-wide architecture context for Copilot/agents |

## Agents (`.github/agents/`)

| Agent | Use for |
|-------|---------|
| `code-reviewer` | General code review |
| `coding-agent` | Implementing features/fixes end-to-end |
| `security-analyst` | Security review and threat analysis |
| `technical-writer` | Docs, READMEs, changelogs |
| `terraform-reviewer` | Reviewing Terraform / IaC |
| `test-engineer` | Writing and improving tests |

## Instructions (`.github/instructions/`)

Scoped standards applied by `applyTo` glob: `git-workflow`, `makefile`, `tool-shell`,
`assist-code-review`, `assist-markdown`, `assist-security`, and `best-practices-*` for Docker,
GitHub Actions, JavaScript, and Python, plus the `guideline-JPL_Coding_Standard_C` reference.

## Skills (`.github/skills/`)

Invoke a skill when its task matches. Highlights:

- **Governance / AI**: `agentic-workflows`, `resolve-issue-pr`, `security-remediation`
- **Git & GitHub**: `git-commit`, `git-flow-branch-creator`, `gh-cli`, `github-issues`
- **Python**: `pytest-coverage`, `ruff-recursive-fix`, `python-mcp-server-generator`
- **Refactoring**: `refactor`, `refactor-plan`, `refactor-method-complexity-reduce`,
  `review-and-refactor`
- **Docker / supply chain**: `multi-stage-dockerfile`, `dependabot`, `dependency-track`,
  `gitguardian`
- **Docs / misc**: `readme-blueprint-generator`, `repo-story-time`, `meeting-minutes`,
  `github-copilot-starter`

Each skill is a `SKILL.md` (name + description frontmatter) with optional `references/` and
`scripts/`. See a skill's own file for its procedure.

## Conventions

- These assets are **org-neutral**: they describe *how* to work, not any single downstream app.
  Repo-specific grounding belongs in that repo's own `AGENTS.md`.
- Skills must not contain secrets, credentials, or references to private/other-org repositories.
