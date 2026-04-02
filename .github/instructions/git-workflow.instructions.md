---
applyTo: "**"
---

# Git Workflow Best Practices

This organization follows a Gitflow-inspired branching strategy. All contributors must adhere to these standards when managing the codebase, branches, and commits.

## Branch Strategy

### Branch Naming

| Branch Type | Pattern | Purpose |
|-------------|---------|---------|
| Production | `main` | Latest stable production code — never commit directly |
| Development | `dev` | Integration branch; aggregates features before release |
| Feature | `feat/<short-description>` | New features or enhancements |
| Release | `rel/<version>` | Release preparation and stabilization |
| Hotfix | `fix/<short-description>` | Urgent production patches |
| Dependency updates | `renovate/<package-name>` | Automated dependency updates via Renovate |

**Rules:**
- Use lowercase and hyphens only in branch names (`feat/user-auth`, not `feat/UserAuth` or `feat/user_auth`)
- Keep branch names short but descriptive (max 50 characters)
- Delete branches after merge; never leave stale branches open for more than 30 days

### Branch Protection

- `main` and `dev` are protected branches — force pushes and direct commits are forbidden
- All changes to `main` must come through `rel/*` or `fix/*` branches via pull request
- All changes to `dev` must come through `feat/*`, `rel/*`, or `fix/*` via pull request
- At least one approving review is required before merging

## Commit Conventions

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | When to Use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code change that is neither a fix nor a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `chore` | Maintenance tasks, dependency updates, build changes |
| `ci` | CI/CD pipeline changes |
| `revert` | Revert a previous commit |

### Commit Message Rules

- Use the imperative mood in the summary line: "Add feature" not "Added feature"
- Keep the summary line under 72 characters
- Separate the summary from the body with a blank line
- Reference issue numbers in the footer: `Closes #123` or `Refs #456`
- One logical change per commit — avoid "kitchen sink" commits
- Never use `git commit -m "WIP"` or `git commit -m "fix"` — always provide context

**Good examples:**
```
feat(auth): add OAuth2 login with GitHub provider

Implements GitHub OAuth2 flow using authlib. Stores token in
the session and fetches user profile on first login.

Closes #42
```

```
fix(api): handle empty payload in /webhooks endpoint

Adds an early return with HTTP 400 when the request body is
missing or cannot be parsed as JSON.

Refs #88
```

**Bad examples:**
```
fixed stuff
update
WIP
misc changes
```

## Pull Request Guidelines

- **Title**: Follow the same Conventional Commits format as commit messages
- **Description**: Fill out the PR template completely — explain *what* changed and *why*
- **Size**: Keep PRs focused; aim for under 400 lines changed. Split large changes into smaller, logical PRs
- **Draft PRs**: Use draft status while work is in progress; only mark ready when tests pass and the PR is truly ready for review
- **Review turnaround**: Reviewers should respond within one business day
- **Merge strategy**:
  - `feat/*` → `dev`: Squash and merge (clean history)
  - `rel/*` → `main`: Merge commit (preserve release history)
  - `fix/*` → `main` and `dev`: Cherry-pick or merge commit

## Tagging and Releases

- Tags follow [Semantic Versioning](https://semver.org/): `vMAJOR.MINOR.PATCH`
- Tags are created only on `main` after a successful release merge
- Annotated tags must include a short release summary: `git tag -a v1.2.0 -m "Release v1.2.0: add OAuth2 login"`
- Never delete or move existing tags

## General Rules

- **Never rewrite public history** — no force-push on shared branches
- **Keep `dev` always green** — failing CI on `dev` is a P1 issue
- **Sync regularly** — rebase feature branches from `dev` at least daily to minimize merge conflicts
- **No secrets in commits** — use `.env` files excluded by `.gitignore`; rotate any secret accidentally committed immediately
