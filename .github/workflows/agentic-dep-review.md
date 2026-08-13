---
on:
  pull_request:
    types: [opened, synchronize]
permissions:
  contents: read
  pull-requests: read
engine: claude
network: defaults
if: |
  github.actor == 'dependabot[bot]' ||
  github.actor == 'renovate[bot]' ||
  startsWith(github.head_ref, 'renovate/') ||
  startsWith(github.head_ref, 'dependabot/')
safe-outputs:
  add-comment:
    max: 1
  add-labels:
    max: 2
tools:
  github:
    toolsets:
      - default
    allowed:
      - get_pull_request
      - get_pull_request_files
      - get_pull_request_diff
---

# Review a dependency-update pull request

This PR was opened by Dependabot or Renovate. Summarize the change and surface anything a human
reviewer should look at before merging.

## Task

1. Read the PR diff — identify the package(s), the from → to versions, and the ecosystem
   (GitHub Actions, uv/pip, npm, Docker, pre-commit, Terraform, Helm).
2. Post **one** comment with:
   - a one-line summary of what is being bumped,
   - the jump type (patch / minor / major) and whether it is likely breaking,
   - any security relevance (does the bump reference a CVE / GHSA advisory?),
   - a clear recommendation: `safe to automerge`, `review changelog`, or `needs manual testing`.
3. Optionally add up to two existing labels (`dependencies`, and one of the ecosystem labels
   such as `github-actions`, `python`, `docker`) if not already present.

Do not approve or merge the PR. Keep the comment short and skimmable.
