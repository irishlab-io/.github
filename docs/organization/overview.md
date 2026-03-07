---
hide:
  - toc
---

# GitHub Organization Setup (Opinionated)

This guide is an opinionated baseline for setting up a secure, scalable GitHub organization for small-to-mid engineering teams.

## Principles

- **Security by default**: private repos, SSO required, 2FA required, secret scanning enabled.
- **Separation of duties**: no shared owner account, teams own access, least privilege first.
- **Reusable automation**: shared workflows and composite actions in a dedicated `.github` repository.
- **Fast feedback**: branch and PR pipelines run early and consistently.
- **Governance as code**: rulesets, CODEOWNERS, and repository templates are versioned.

## Target Operating Model

Use this org layout as the default:

```text
<org>/
├── .github                     # org-wide workflows, issue/PR templates, docs
├── platform-infra              # infra modules and platform automation
├── product-api                 # backend services
├── product-web                 # frontend apps
├── product-mobile              # mobile apps (if applicable)
├── shared-libraries            # internal packages
└── sandbox-*                   # short-lived experimentation repos
```

## Bootstrap Sequence

### 1) Create and secure the organization

In **Settings → Security**:

- Require **two-factor authentication**.
- Require **SAML SSO** (if using Enterprise/IdP integration).
- Restrict repository creation to approved roles.
- Default repository visibility to **Private**.
- Enable **secret scanning** and **push protection** for all repositories.
- Enable **Dependabot alerts** and **Dependabot security updates**.

### 2) Define teams and permissions

Create teams aligned to ownership boundaries:

- `org-admins` (very small group)
- `platform`
- `backend`
- `frontend`
- `security`
- `qa`

Default permission model:

- No direct repo access for individual users unless justified.
- Teams get `read`/`write`/`maintain` by need.
- `admin` access is rare and audited.

### 3) Establish repository taxonomy

Adopt naming conventions:

- Services: `svc-<domain>-<name>`
- Libraries: `lib-<language>-<name>`
- Infrastructure: `infra-<scope>-<name>`
- Experiments: `sandbox-<owner>-<topic>`

Repository defaults:

- Branch names: `main`, `dev`.
- Default labels: `type:*`, `priority:*`, `area:*`.
- Required files: `README.md`, `CODEOWNERS`, `SECURITY.md`, `LICENSE`.

### 4) Install governance controls

Use **organization rulesets** instead of only per-repo branch protection.

Required baseline for `main`:

- Pull request required before merge.
- 1-2 approving reviews (2 for critical repos).
- Dismiss stale reviews on new commits.
- Require status checks to pass.
- Require conversation resolution before merge.
- Block force-push and deletion.
- Require linear history (optional but recommended).

### 5) Standardize CI/CD through `.github`

In the org `.github` repository:

- Add reusable workflows for `lint`, `test`, `build`, `scan`, and `release`.
- Add composite actions for repeated setup logic.
- Add issue/PR templates and contributing standards.
- Version and document all shared workflow contracts.

### 6) Enforce secure supply chain defaults

Across all repos:

- Enable Dependabot for ecosystem updates.
- Pin third-party GitHub Actions by SHA.
- Generate SBOM for production artifacts.
- Run SAST/SCA/container scan in CI.
- Gate merges on critical vulnerabilities.

### 7) Roll out in waves

Recommended rollout:

1. Platform and security repositories
2. Core product repositories
3. Shared libraries and tooling
4. Sandbox/legacy repositories

Treat non-compliant repositories as exceptions with explicit expiry dates.

## Pull Request Policy (Default)

Use this default PR policy everywhere unless a documented exception exists:

- Small PRs (prefer <300 changed lines).
- At least one code owner review.
- CI green before merge.
- Squash merge for product repos.
- Conventional commits (recommended).

## Default Branch Strategy

Use this branch strategy:

- `main`: production-ready code
- `dev`: integration branch
- `feat/*`: features
- `fix/*`: bug fixes
- `rel/*`: release preparation
- `hotfix/*`: urgent production patch

## Day-2 Operations

Run these continuously:

- Quarterly permission review for teams and admins.
- Monthly ruleset and required-check audit.
- Weekly dependency and action pinning review.
- Incident postmortems with policy updates.
- Documentation refresh with every governance change.

## Definition of Done for Organization Setup

An organization is considered “set up” when:

- Security defaults are enforced org-wide.
- Teams and least-privilege permissions are in place.
- Rulesets protect default branches in all critical repos.
- Shared workflows are adopted by active repositories.
- Code ownership and review policies are enforced.
- Vulnerability and dependency management are operational.

## Related Documents

- [Pipeline Overview](../pipeline/overview.md)
- [Branches Pipeline](../pipeline/branches.md)
- [Dependabot](../pipeline/dependabot.md)
- [Security Overview](../security/overview.md)
