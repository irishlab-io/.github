---
name: AW - Policy Orchestrator
run-name: "Agentic Workflows - Policy Orchestrator by ${{ github.actor }}"

on:
  push:
    branches:
      - main
    paths:
      - "docs/policy/**.md"
  workflow_dispatch:

engine:
  id: copilot

permissions:
  contents: read
  issues: read
  pull-requests: read

model: gpt-5.4-mini

network:
  allowed:
    - defaults

safe-outputs:
  create-issue:
    max: 1
    title-prefix: "[policy]: "
  dispatch-workflow:
    workflows:
      - aw-policy-worker
    max: 10
  report-failure-as-issue: false

timeout-minutes: 15

tools:
  github:
    toolsets:
      - default
      - search
    allowed:
      - get_file_contents
      - get_repository
      - search_repositories
---

# Policy fan-out orchestrator

You are the **orchestrator** in an OrchestratorOps fan-out. You do not analyse any target repository yourself — you decide *what changed*, *who is affected*, and dispatch one worker per target. The workers do the per-repo analysis, and they are the ones that adopt the architect agent; you never interpret policy text into activities yourself.

## Task

1. **Identify the policy in play.** Read the policy files under `docs/policy/` in this repository. On a `push` trigger, restrict yourself to the files that changed in this push. On a manual `workflow_dispatch`, consider every policy whose frontmatter `status` is `active`. Skip any policy that is not `active`.
2. **Read the target list** from `.github/policy-targets.yml` in this repository. The `targets` list is authoritative — do not invent targets, do not enumerate the org yourself, and do not dispatch to anything absent from that list.
3. **Mint a tracker id** of the form `policy-${{ github.run_id }}`. It correlates this run's tracking issue with every issue the workers file, so it must be identical everywhere it appears.
4. **Open one tracking issue** in this repository. Title it with the policy id and title. The body must contain the tracker id, the policy path, and a Markdown table of `target repo | dispatched (yes/no) | reason if not`, sorted alphabetically.
5. **Dispatch one worker per target**, up to the configured maximum of 10 per run. Each dispatch targets the `aw-policy-worker` workflow with inputs:
   - `target_repo` — the `owner/repo` slug from the target list
   - `policy_path` — the path of the policy file, e.g. `docs/policy/hello-world.md`
   - `tracker_id` — the tracker id from step 3

If there are more targets than the dispatch limit allows, dispatch the first 10 alphabetically and say plainly in the tracking issue which targets were deferred and that a re-run is needed.

## Constraints

- **Read-only.** You never modify this repository or any other. Your only outputs are the single tracking issue and the worker dispatches.
- If no `active` policy changed, emit no dispatches and no issue — an empty run is the correct outcome, not something to report.
- Never dispatch the same target twice in one run.
