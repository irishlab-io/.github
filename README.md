# .github

This repository manage organization gouvernance, reusable workflow, references models, to be used by other repos from within this organization.

This is for demonstration purpose.

## Gouvernance

### Repos

Still a WIP. ##TODO: Get this working

### Rulesets

- `main.json`: Typical `main` branch rulesets, nothing special
- `tag.json`: Typical project `tag` rulesets, nothing special

## References

Something about `copilot-instructions.md`

### Agents

- code-reviewer.md
- coding-agent.md
- security-analyst.md
- technical-writer.md
- terraform-reviewer.md
- test-engineer.md

### Instructions

### Skills

TBD

### Workflows

This project follows a minor variation of the Gitflow branches naming convention:

- Main branch: Stores the latest production codebase, named **main**
- Develop branch: Aggregates features and developments, named **dev**
- Feature branches: Used to develop new features, named **feat/***
- Release branches: Used to manage the release process, named **rel/***
- Hotfix branches: Used to quickly patch production releases, named **fix/***
- Renovate branches: Used to update dependencies with [Renovate](https://www.mend.io/renovate/), named **renovate/***


## Settings

Safe Setting repo template
