---
title: Organization Bootstrap Checklist
---

# Organization Bootstrap Checklist

Use this checklist to execute setup quickly and consistently.

## Identity and Access

- [ ] Require 2FA for all members
- [ ] Enforce SSO (if available)
- [ ] Disable direct owner usage for daily work
- [ ] Create `org-admins`, `platform`, `security`, and product teams
- [ ] Assign least-privilege team permissions

## Repository Standards

- [ ] Create `.github` repository for shared standards
- [ ] Add PR template, issue templates, and `SECURITY.md`
- [ ] Add `CODEOWNERS` to all critical repositories
- [ ] Define repository naming conventions
- [ ] Set default branch policy (`main` + protected)

## Rulesets and Review Policy

- [ ] Require pull requests before merge
- [ ] Require approving review(s)
- [ ] Require status checks to pass
- [ ] Block force pushes and deletion
- [ ] Require conversation resolution

## CI/CD and Supply Chain

- [ ] Adopt reusable workflows from `.github`
- [ ] Pin all third-party actions by SHA
- [ ] Enable Dependabot alerts and security updates
- [ ] Enable secret scanning and push protection
- [ ] Add SAST/SCA/container scanning in CI

## Rollout and Governance

- [ ] Apply baseline controls to tier-1 repos first
- [ ] Track exceptions with owners and expiration date
- [ ] Run first access review within 30 days
- [ ] Publish ownership map for all active repos
- [ ] Define incident and escalation process

## Exit Criteria

- [ ] All production repositories meet baseline controls
- [ ] Exception register is documented and approved
- [ ] Setup guide is linked from docs home
