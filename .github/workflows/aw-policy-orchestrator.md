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
      # gh-aw's installer only writes /usr/local/bin/copilot on a toolcache MISS. On a HIT it merely prepends /opt/hostedtoolcache/... to PATH, but the sandbox spawns the CLI via the hardcoded absolute path /usr/local/bin/copilot and refuses to mount the toolcache when it sits under /opt. Without this shim, any runner with a warm copilot-cli cache fails with: spawn /usr/local/bin/copilot ENOENT.
      # This script is duplicated in pre-agent-steps (agent job) and safe-outputs.threat-detection.steps (detection job) of both aw-policy-orchestrator.md and aw-policy-worker.md. Keep the four copies identical. It cannot live in .github/scripts/ because the detection job checks out the repo only conditionally.
      if [ -x /usr/local/bin/copilot ]; then
        echo "/usr/local/bin/copilot already present - nothing to do"
        exit 0
      fi
      resolved="$(command -v copilot || true)"
      if [ -z "$resolved" ]; then
        # In the detection job this step is injected BEFORE 'Install GitHub Copilot CLI', so PATH is not populated yet. Look in the toolcache directly.
        resolved="$(find "${RUNNER_TOOL_CACHE:-/opt/hostedtoolcache}/copilot-cli" -maxdepth 4 -type f -name copilot -perm -u+x 2>/dev/null | sort -V | tail -1)"
      fi
      if [ -z "$resolved" ]; then
        # Nothing cached either, so the installer has not run yet and will take the toolcache-miss path, which installs to /usr/local/bin itself. Nothing to do.
        echo "No Copilot CLI found yet; leaving it to the installer's toolcache-miss path"
        exit 0
      fi
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
  threat-detection:
    # The detection verdict is a judgement call. On gpt-5.4-mini (inherited from the
    # workflow's top-level model) it false-positived on this workflow's own legitimate
    # instructions, while itself noting they "align with the workflow's own legitimate
    # orchestrator instructions". Give the judge a stronger model than the agent it judges.
    engine:
      id: copilot
      model: gpt-5.4
    steps:
      - name: Materialize Copilot CLI at the sandbox spawn path
        shell: bash
        run: |
          set -euo pipefail
          # gh-aw's installer only writes /usr/local/bin/copilot on a toolcache MISS. On a HIT it merely prepends /opt/hostedtoolcache/... to PATH, but the sandbox spawns the CLI via the hardcoded absolute path /usr/local/bin/copilot and refuses to mount the toolcache when it sits under /opt. Without this shim, any runner with a warm copilot-cli cache fails with: spawn /usr/local/bin/copilot ENOENT.
          # This script is duplicated in pre-agent-steps (agent job) and safe-outputs.threat-detection.steps (detection job) of both aw-policy-orchestrator.md and aw-policy-worker.md. Keep the four copies identical. It cannot live in .github/scripts/ because the detection job checks out the repo only conditionally.
          if [ -x /usr/local/bin/copilot ]; then
            echo "/usr/local/bin/copilot already present - nothing to do"
            exit 0
          fi
          resolved="$(command -v copilot || true)"
          if [ -z "$resolved" ]; then
            # In the detection job this step is injected BEFORE 'Install GitHub Copilot CLI', so PATH is not populated yet. Look in the toolcache directly.
            resolved="$(find "${RUNNER_TOOL_CACHE:-/opt/hostedtoolcache}/copilot-cli" -maxdepth 4 -type f -name copilot -perm -u+x 2>/dev/null | sort -V | tail -1)"
          fi
          if [ -z "$resolved" ]; then
            # Nothing cached either, so the installer has not run yet and will take the toolcache-miss path, which installs to /usr/local/bin itself. Nothing to do.
            echo "No Copilot CLI found yet; leaving it to the installer's toolcache-miss path"
            exit 0
          fi
          root="$(dirname "$(dirname "$resolved")")"
          echo "Copying Copilot CLI install root ${root} -> /usr/local/lib/copilot-cli"
          sudo rm -rf /usr/local/lib/copilot-cli
          sudo cp -a "$root" /usr/local/lib/copilot-cli
          printf '#!/usr/bin/env bash\nexec /usr/local/lib/copilot-cli/bin/copilot "$@"\n' | sudo tee /usr/local/bin/copilot >/dev/null
          sudo chmod 0755 /usr/local/bin/copilot
          /usr/local/bin/copilot --version

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
4. **Open one tracking issue** in this repository. Title it with the policy id and title. The body contains the tracker id, the policy path, and a Markdown table of `target repo | dispatch requested (yes/no) | reason if not`, sorted alphabetically. The table records what you requested, since the outcome is not known during this run.
5. **Request one worker per target**, up to the configured maximum of 10 per run. Two dispatch tools are available and they take different argument layouts. The correct one here is **`aw_policy_worker`**: it is already bound to the worker workflow and accepts these three values directly, all required on every call.
   - `target_repo` — the `owner/repo` slug from the target list
   - `policy_path` — the path of the policy file, e.g. `docs/policy/hello-world.md`
   - `tracker_id` — the tracker id from step 3

   The general-purpose `dispatch_workflow` tool expects a different layout and is not the right fit for this step.

If there are more targets than the per-run maximum allows, take the first 10 alphabetically and note in the tracking issue which targets were deferred and that a re-run is needed.

## Constraints

- **Read-only.** You never modify this repository or any other. Your results are the single tracking issue and the worker requests.
- **Report what you requested, not what resulted.** Your results are applied after this run ends, so you cannot see whether any of them succeeded. Describe them as requested or submitted — in the tracking issue and in your closing summary alike.
- If no `active` policy changed, produce nothing — an empty run is the correct outcome, not something to report.
- One request per target, at most, in a single run.
