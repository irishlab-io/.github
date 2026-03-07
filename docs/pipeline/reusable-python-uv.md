---
hide:
  - toc
---

# Reusable - Python UV

## What

This reusable workflow installs [uv](https://docs.astral.sh/uv/), sets up the requested Python version(s), installs project dependencies, builds the package, and optionally runs [Pytest](https://pytest.org/) — including [Playwright](https://playwright.dev/python/) browser tests. It supports both single-version and matrix builds across multiple Python versions and operating systems.

## Why

Python projects require a consistent, reproducible build-and-test environment. By centralising the uv install, dependency sync, and test execution in one reusable workflow, every project benefits from the same caching strategy, matrix configuration, and Playwright support without duplicating boilerplate. Using `uv` keeps dependency resolution fast and deterministic.

## How

Call this workflow from any Python project managed with `uv` and `pyproject.toml`.

### Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `os` | Runner OS for a single-OS build | No | `ubuntu-24.04` |
| `os-matrix` | JSON array of OS labels for a matrix build | No | `""` |
| `playwright-enable` | Install Playwright browsers before running Pytest | No | `false` |
| `pytest-enable` | Run Pytest after the build | No | `true` |
| `pytest-marker-included` | Pytest `-m` marker expression to **include** | No | `""` |
| `pytest-marker-excluded` | Pytest `-m` marker expression to **exclude** | No | `""` |
| `python-version` | Python version for a single-version build | No | `3.14` |
| `python-version-matrix` | JSON array of Python versions for a matrix build | No | `""` |
| `uv-cache` | Enable uv layer caching | No | `true` |
| `uv-version` | uv version to install | No | `latest` |
| `working_directory` | Project working directory | No | `""` |

### Secrets

None required.

### Example — Single version

```yaml
jobs:
  build:
    name: Python Build & Test
    uses: irishlab-io/.github/.github/workflows/reusable-python-uv.yml@main
    with:
      python-version: "3.13"
      pytest-enable: true
```

### Example — Multi-version matrix

```yaml
jobs:
  build:
    name: Python Build & Test
    uses: irishlab-io/.github/.github/workflows/reusable-python-uv.yml@main
    with:
      python-version-matrix: '["3.12", "3.13"]'
      os-matrix: '["ubuntu-24.04", "ubuntu-24.04-arm"]'
```

### Example — With Playwright

```yaml
jobs:
  e2e:
    name: Python E2E Tests
    uses: irishlab-io/.github/.github/workflows/reusable-python-uv.yml@main
    with:
      python-version: "3.13"
      playwright-enable: true
      pytest-marker-included: "e2e"
```
