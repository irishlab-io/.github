---
title: Baseline Policy Template
---

# Baseline Governance Policy Template

Copy this template into an internal policy page and adapt values to your organization.

## 1. Scope

This policy applies to all repositories under the GitHub organization, with stricter controls for production and security-sensitive repositories.

## 2. Access Control

- Access is granted to teams, not individuals, wherever possible.
- Organization owner role is restricted to a minimal set of platform administrators.
- Elevated access requires documented approval and periodic review.

## 3. Branch and Merge Controls

- Direct pushes to protected branches are prohibited.
- Pull requests are mandatory for protected branches.
- At least one code owner review is required.
- Required checks must pass before merge.
- Force push and branch deletion are blocked on protected branches.

## 4. CI/CD and Workflow Security

- Reusable workflows from the `.github` repository are the default.
- Third-party GitHub Actions must be pinned by commit SHA.
- Workflow changes require platform team review.

## 5. Dependency and Vulnerability Management

- Dependabot alerts and security updates must be enabled.
- Secret scanning and push protection must be enabled.
- Critical vulnerabilities block merge unless a time-bound exception is approved.

## 6. Exceptions

Every exception must include:

- Repository name
- Control being waived
- Risk rationale
- Owner
- Expiration date
- Mitigation plan

## 7. Audit Cadence

- Monthly: branch/ruleset and CI baseline checks
- Quarterly: permission and team membership review
- Ad hoc: after incidents or material architecture changes
