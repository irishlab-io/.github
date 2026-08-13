---
on:
  schedule:
    - cron: "17 7 * * 1"
  workflow_dispatch:
permissions:
  contents: read
engine: claude
network: defaults
safe-outputs:
  create-issue:
    max: 1
    title-prefix: "[governance] "
    labels: [area:infra, type:maintenance]
tools:
  github:
    toolsets:
      - default
      - labels
      - search
    allowed:
      - search_repositories
      - get_repository
      - list_labels
      - get_file_contents
---

# Weekly org repository governance audit

You audit the `irishlab-io` organization's repositories for drift from the org standards defined
in this repository and report findings as a single tracking issue.

## Standards (source of truth in `irishlab-io/.github`)

- Branch protection ruleset: `.github/rulesets/main.json`
- Tag protection ruleset: `.github/rulesets/tag.json`
- Standard labels: `.github/labels.yml`

## Task

1. List the org's active, non-archived, non-template repositories.
2. For each, compare its branch/tag rulesets and labels against the standards above. Flag:
   - missing or weaker `main` branch protection (no PR requirement, signatures off, deletion allowed),
   - missing tag protection,
   - missing standard labels.
3. Emit **one** issue titled with a date, containing a compact Markdown table of
   `repo | drift found | suggested fix`, sorted most-severe first. If nothing drifted, say so in
   one line and still open the issue as a green "no drift" record.

Skip the `.github` repo itself. Read only — never modify any repository directly; the issue is
the deliverable a maintainer acts on.
