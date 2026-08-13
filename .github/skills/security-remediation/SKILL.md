---
name: security-remediation
description: Remediate an already-identified security finding (from a SAST/SCA tool, Dependabot, or a human report) in code. Use for security-labelled issues. This is not a vulnerability scanner.
---

# Security remediation (known findings)

Use this skill for `security`-labelled issues. The vulnerability has **already been identified** —
by a SAST/SCA tool (Snyk, SonarQube, CodeQL, …), by Dependabot, or by a human — and is described
in the issue. Your job is to **remediate the reported finding in code**, not to scan the
repository for new vulnerabilities.

Follow responsible-disclosure practice: keep exploit detail proportionate and out of public
channels unless the target repository explicitly documents that it is a deliberately vulnerable
teaching/demo app.

## Scope: in-code fixes only

- Fix the **code** that is vulnerable.
- **Do not** bump dependencies or edit manifests/lockfiles (`pyproject.toml`, `uv.lock`,
  `package-lock.json`, `requirements.txt`, …) to resolve a version/SCA finding — Dependabot/Renovate
  own routine dependency updates.
- If the issue is purely a vulnerable-dependency / SCA finding (no code change would fix it), say
  so in the PR description and the issue comment and **defer to Dependabot/Renovate** rather than
  bumping versions yourself.

## Procedure

1. **Parse the finding.** From the issue, identify the CWE (and CVE, if any), the severity, and
   the affected file/component. Then read that code to confirm the root cause and how it is reached.
2. **Apply the standard fix pattern** for the weakness (below), matching the repo's conventions and
   architecture.
3. **Update the matching security test** to assert the vulnerability is now fixed (e.g. that an
   injection payload is rejected) instead of asserting the old vulnerable behaviour. Keep the suite
   and the repo's coverage gate green.
4. **Open a detailed PR** (see the `resolve-issue-pr` quality bar) with the PR title prefixed
   `[security]`. In addition to the standard sections, document: the **CWE/CVE**, a **severity**
   rating with justification (impact × exploitability), the **root cause and how it could be
   exploited**, and the **exact remediation** applied with references to the changed lines.

## CWE → fix-pattern reference

| Weakness | Standard remediation |
|----------|----------------------|
| SQL injection | Parameterized queries or an ORM; never string-concatenate input into SQL |
| Insecure deserialization | Remove `pickle`/native deserialization on untrusted data; use safe formats/loaders |
| Command injection | Use a subprocess API with an argument list; never `os.system` / shell strings with input |
| Path traversal | Normalise and validate paths against an allowed base directory; reject `..` escapes |
| Weak crypto | Use modern algorithms/libraries; no hardcoded keys or DES/MD5-style primitives |
| XXE | Use a safe XML parser with external entities disabled |
| SSRF | Validate/allowlist outbound destinations |
| XSS | Rely on template autoescaping; escape untrusted output |
| CSRF | Use the framework's CSRF protection on state-changing endpoints |
| IDOR / broken auth | Enforce ownership/authorization checks; do not auto-elevate privileges |
