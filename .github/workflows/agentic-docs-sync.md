---
on:
  push:
    branches: [main]
    paths:
      - ".github/workflows/**"
      - ".github/rulesets/**"
      - ".github/labels.yml"
      - "repos/**"
  workflow_dispatch:
permissions:
  contents: read
engine: claude
network: defaults
safe-outputs:
  create-pull-request:
    max: 1
    draft: true
    title-prefix: "docs: "
    labels: [type:docs, area:docs]
tools:
  github:
    toolsets:
      - default
    allowed:
      - get_file_contents
---

# Keep documentation in sync with configuration

Workflow, ruleset, label, or repo-definition files just changed on `main`. Your job is to catch
documentation that has fallen out of sync and open a draft PR that fixes it.

## Task

1. Read the changed configuration files and the docs that describe them:
   `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`, and `docs/`.
2. Find concrete mismatches, for example:
   - a `reusable-*.yml` named in docs that no longer exists (or a new one that is undocumented),
   - a path that moved (e.g. `rulesets/` vs `.github/rulesets/`),
   - a label or input documented that no longer matches `.github/labels.yml` or the workflow's
     `workflow_call` inputs.
3. If you find fixable mismatches, open **one** draft PR that edits only documentation to match
   reality. Keep the diff minimal and factual. If everything is already in sync, do nothing and
   emit no PR.

Never change workflow logic or configuration — documentation edits only.
