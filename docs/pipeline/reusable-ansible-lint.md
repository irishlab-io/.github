---
hide:
  - toc
---

# Reusable - Ansible Lint

## What

This reusable workflow runs [ansible-lint](https://ansible.readthedocs.io/projects/lint/) against your Ansible codebase to detect common mistakes, enforce best practices, and ensure compliance with Ansible coding standards.

## Why

Ansible playbooks and roles can accumulate subtle mistakes that are hard to catch during code review alone. Running `ansible-lint` automatically in CI enforces a consistent style, catches syntax errors, deprecated modules, and unsafe patterns before they reach production, reducing operational risk in infrastructure automation.

## How

Call this workflow from any repository that contains Ansible content by referencing it with `workflow_call`.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `configuration_file` | Path to an `ansible-lint` configuration file | No | `""` |
| `setup_python` | Automatically set up Python before running lint | No | `true` |
| `requirements_file` | Path to Ansible Galaxy requirements file | No | `""` |
| `working_directory` | Project directory containing Ansible content | No | `""` |

### Secrets

None required.

### Example

```yaml
jobs:
  ansible-lint:
    name: Ansible Lint
    uses: irishlab-io/.github/.github/workflows/reusable-ansible-lint.yml@main
    with:
      configuration_file: ".ansible-lint"
      requirements_file: "requirements.yml"
      working_directory: "ansible/"
```
