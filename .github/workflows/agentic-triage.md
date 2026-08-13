---
on:
  issues:
    types: [opened, reopened]
  pull_request:
    types: [opened, reopened]
permissions:
  contents: read
  issues: read
  pull-requests: read
engine: claude
network: defaults
safe-outputs:
  add-labels:
    max: 4
  add-comment:
    max: 1
tools:
  github:
    toolsets:
      - default
    allowed:
      - issue_read
      - get_pull_request
      - list_issues
---

# Triage new issues and pull requests

You triage an incoming issue or pull request for the `irishlab-io` organization.

## Context

- Event: `${{ github.event_name }}`
- Repository: `${{ github.repository }}`
- Number: `${{ github.event.issue.number || github.event.pull_request.number }}`

## Task

1. Read the title and body of the triggering issue/PR.
2. Choose **1–4 labels** from the org's standard label set (defined in
   `irishlab-io/.github`'s `.github/labels.yml`). Prefer one `type:*` label, and add
   `priority:*` / `area:*` labels only when the content clearly justifies them. Only apply labels
   that already exist in the repository.
3. Post **one** concise comment (2–4 sentences) that summarizes the report and, if useful, asks
   for the single most important missing detail (repro steps, expected vs actual, affected repo).

Do not restate the whole body. Do not close, assign, or edit anything — emit only labels and the
comment via safe-outputs.
