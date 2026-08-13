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

pre-agent-steps:
  - name: Materialize Copilot CLI at the sandbox spawn path
    shell: bash
    run: |
      set -euo pipefail
      # gh-aw's installer only writes /usr/local/bin/copilot on a toolcache MISS. On a HIT it merely prepends /opt/hostedtoolcache/... to PATH, but the sandbox spawns the agent via the hardcoded absolute path /usr/local/bin/copilot and refuses to mount the toolcache when it sits under /opt. Without this shim, any runner with a warm copilot-cli cache fails with: spawn /usr/local/bin/copilot ENOENT.
      if [ -x /usr/local/bin/copilot ]; then
        echo "/usr/local/bin/copilot already present (installer took the toolcache-miss path)"
        exit 0
      fi
      resolved="$(command -v copilot || true)"
      if [ -z "$resolved" ]; then
        echo "::error::copilot CLI not found on PATH; cannot materialize it for the sandbox"
        exit 1
      fi
      # Copy the whole versioned install root under /usr/local (which the sandbox can see), so this holds whether or not the launcher is self-contained.
      root="$(dirname "$(dirname "$resolved")")"
      echo "Copying Copilot CLI install root ${root} -> /usr/local/lib/copilot-cli"
      sudo rm -rf /usr/local/lib/copilot-cli
      sudo cp -a "$root" /usr/local/lib/copilot-cli
      printf '#!/usr/bin/env bash\nexec /usr/local/lib/copilot-cli/bin/copilot "$@"\n' | sudo tee /usr/local/bin/copilot >/dev/null
      sudo chmod 0755 /usr/local/bin/copilot
      /usr/local/bin/copilot --version

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
4. **Open one tracking issue** in this repository. Title it with the policy id and title. The body must contain the tracker id, the policy path, and a Markdown table of `target repo | dispatch requested (yes/no) | reason if not`, sorted alphabetically. Record what you *requested*, not what succeeded — dispatches are carried out after your run finishes, so you never observe their outcome. Never write a table that asserts a dispatch completed.
5. **Dispatch one worker per target**, up to the configured maximum of 10 per run. Call the dedicated **`aw_policy_worker`** tool once per target, passing exactly these three arguments:
   - `target_repo` — the `owner/repo` slug from the target list
   - `policy_path` — the path of the policy file, e.g. `docs/policy/hello-world.md`
   - `tracker_id` — the tracker id from step 3

Use that tool. Do **not** hand-construct dispatch JSON and do **not** pipe a payload into the generic `safeoutputs dispatch_workflow` shell command — the two take different shapes, and a flattened payload silently dispatches with no inputs at all, which GitHub then rejects with `Required input 'policy_path' not provided`. If for any reason you must fall back to the generic form, the workflow inputs belong **nested under an `inputs` object**, like `{"type":"dispatch_workflow","workflow":"aw-policy-worker","inputs":{"target_repo":"...","policy_path":"...","tracker_id":"..."}}` — never at the top level.

If there are more targets than the dispatch limit allows, dispatch the first 10 alphabetically and say plainly in the tracking issue which targets were deferred and that a re-run is needed.

## Constraints

- **Read-only.** You never modify this repository or any other. Your only outputs are the single tracking issue and the worker dispatches.
- **Use the provided tools, not the shell.** Every output you need has a dedicated tool with a validated schema. Hand-built JSON piped into a `safeoutputs` command bypasses that validation and fails silently or partially.
- If no `active` policy changed, emit no dispatches and no issue — an empty run is the correct outcome, not something to report.
- Never dispatch the same target twice in one run.
