# Repository Requests

This directory is the **source of truth** for all repositories in the
`irishlab-io` organization. Each YAML file describes one repository.

## Requesting a New Repository

1. **Copy the template** — duplicate `_template.yml` and name it after your
   desired repository (e.g. `svc-payments-api.yml`).
2. **Fill in all required fields** — see field documentation inside the
   template.
3. **Open a Pull Request** — use the **"Repository Request"** PR template.
4. **Get the PR approved** — at least one `org-admins` team member must
   approve.
5. **Merge** — once merged to `main`, the repository is created automatically
   and onboarded with standard settings, rulesets, labels, and Dependabot.

## Naming Conventions

| Type | Pattern | Example |
| ---- | ------- | ------- |
| Service | `svc-<domain>-<name>` | `svc-payments-api` |
| Library | `lib-<language>-<name>` | `lib-python-utils` |
| Infrastructure | `infra-<scope>-<name>` | `infra-aws-platform` |
| Sandbox | `sandbox-<owner>-<topic>` | `sandbox-alice-ml` |

## Modifying an Existing Repository

Updating a field in an existing YAML file and merging to `main` will **re-apply**
the changed configuration to the repository (settings, description, topics).
It will **not** re-create the repository if it already exists.

## Offboarding and Deletion

Deleting a repository definition file from this directory and merging that change
to `main` will offboard and permanently delete the matching GitHub repository.

- `repos/test-a.yml` deleted ⟶ `irishlab-io/test-a` deleted
- The repository name is inferred from the deleted file name.
- `_template.yml` is always ignored by the automation.

## Rules

- One YAML file per repository — file name must match the `name` field.
- The `_template.yml` file is ignored by automation.
- Changes to this directory require at least one approval from `org-admins`.
