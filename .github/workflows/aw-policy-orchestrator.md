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
  # No create-issue here on purpose: the orchestrator is a trigger. Every issue the pipeline
  # produces is a worker finding, filed in the repository that finding is about.
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
    post-steps:
      - name: Put the detection verdict on its own line
        if: always()
        shell: bash
        run: |
          set -uo pipefail
          # The detection model sometimes appends its verdict to the end of a narration sentence,
          # e.g. "...behavior in the agent output.THREAT_DETECTION_RESULT:{...}". The parser only
          # matches the marker at the start of a line, so it reports "No THREAT_DETECTION_RESULT
          # found", the conclusion degrades to warning, and the WTD3 warn policy silently aborts
          # every non-reviewable safe output. Split the marker onto its own line before parsing.
          log=/tmp/gh-aw/threat-detection/detection.log
          [ -f "$log" ] || { echo "no detection log at $log; nothing to normalize"; exit 0; }
          if grep -qE '.THREAT_DETECTION_RESULT:' "$log"; then
            sed -i 's/\(.\)THREAT_DETECTION_RESULT:/\1\nTHREAT_DETECTION_RESULT:/g' "$log"
            echo "Normalized: marker moved to the start of its own line"
          else
            echo "Marker already at line start (or absent); no change"
          fi
          grep -n '^THREAT_DETECTION_RESULT:' "$log" | head -1 || echo "note: no line-start marker present after normalization"
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

You are the **orchestrator** in an OrchestratorOps fan-out. Your job is to work out *who is in scope* and request one worker for each of them. Those requests are your deliverable. Each worker evaluates its own repository against every active policy, adopts the architect agent, and files any resulting issue in the repository that issue is about — so you never choose which policies apply, never interpret policy text into activities, and never open an issue.

## Task

1. **Confirm there is work to do.** Read the policy files under `docs/policy/` in this repository and note how many have frontmatter `status: active`. If none are active, stop here and produce nothing. You do not need to decide which of them apply to whom — every worker evaluates all of them.
2. **Read the target list** from `.github/policy-targets.yml` in this repository. The `targets` list is authoritative — do not invent targets, do not enumerate the org yourself, and do not request work for anything absent from that list.
3. **Mint a tracker id** of the form `policy-${{ github.run_id }}`. It correlates this run with every issue the workers file, so it must be identical on every request you make.
4. **Request exactly one worker for each target in the list**, up to the configured maximum of 10 per run. Every target gets a request, regardless of how many policies are active. Each request carries these two values, both required every time:
   - `target_repo` — the `owner/repo` slug from the target list
   - `tracker_id` — the tracker id from step 3

   Two tools can do this and their argument layouts differ. `aw_policy_worker` is bound to the worker workflow already and takes the two values as its own arguments. The general-purpose `dispatch_workflow` tool instead targets workflow `aw-policy-worker` and carries the two values grouped inside its `inputs` argument, not alongside it. Its arguments for one target look like this:

   ```json
   {"workflow": "aw-policy-worker", "inputs": {"target_repo": "irishlab-io/example", "tracker_id": "policy-123"}}
   ```

   The values sit inside `inputs`. Placing them at the top level alongside `workflow` sends a request with no inputs, which the API rejects.

If there are more targets than the per-run maximum allows, take the first 10 alphabetically and say in your closing summary which targets were deferred and that a re-run is needed.

## Constraints

- **Submitting the worker requests is the whole point of this run.** They are the one action you take, and the run has failed if you finish without making them for every eligible target.
- **You change no repository content and open no issues.** Editing files, opening pull requests and filing issues are all outside your remit — findings belong to the workers, in the repositories they concern.
- **A request exists only if you called the tool.** Your closing summary describes the calls you actually made — counting them, naming the targets. A summary that reports requests you did not make is a failed run reported as a success, which is worse than an empty run.
- **Report what you requested, not what resulted.** Your requests are carried out after this run ends, so you cannot see whether any of them succeeded. Describe them as requested or submitted in your closing summary.
- If no policy is `active`, produce nothing — an empty run is the correct outcome, not something to report.
- One request per target, at most, in a single run.
