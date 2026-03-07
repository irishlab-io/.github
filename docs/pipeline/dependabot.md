---
hide:
  - toc
---

# Dependabot

**Dependabot** is a built-in GitHub tool that automates the management of project dependencies, scanning for outdated or vulnerable libraries and automatically creating pull requests (PRs) to update them, helping keep codebases secure and up-to-date with minimal manual effort. It offers Dependabot alerts for known vulnerabilities, security updates to fix them, and version updates to keep all packages current, supporting numerous languages and package managers like npm, pip, and Docker.

**Trigger Conditions:**

- docker: weekly
- github-action: daily
- pip: yearly

For the purpose of this strategy, let's just ignore vanilla recommendation coming from this workflow although it is available and can be leverage in some from.
