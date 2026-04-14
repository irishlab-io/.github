---
description: Python best practices for projects using uv, ruff, and pytest. Enforces PEP 8 compliance, clear docstring conventions, and consistent code quality standards across all Python files.
applyTo: "**/*.py"
---

# Python Best Practices

All Python code in this organization must follow these standards. These guidelines apply to every Python file (`*.py`) across all repositories and are enforced through `ruff` and `pytest`.

## Toolchain

| Tool | Purpose |
|------|---------|
| [`uv`](https://docs.astral.sh/uv/) | Package and project manager |
| [`ruff`](https://docs.astral.sh/ruff/) | Linter and formatter (replaces flake8, isort, black) |
| [`pytest`](https://docs.pytest.org/) | Test runner |

All dependency management must go through `uv`. Never use `pip` directly.

```bash
# Add a runtime dependency
uv add <package>

# Add a development/test dependency
uv add --dev ruff pytest

# Run linter
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Run tests
uv run pytest
```

## Code Style and Formatting (PEP 8)

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all code
- `ruff` is the single source of truth for formatting and linting — do not add `black`, `flake8`, or `isort`
- Maximum line length: **99 characters**
- Use **2 spaces** for indentation — never tabs
- Use **snake_case** for variables, functions, and modules
- Use **PascalCase** for classes
- Use **UPPER_SNAKE_CASE** for module-level constants
- Use **two blank lines** before and after top-level definitions; **one blank line** between methods

### Imports

Organize imports in three groups separated by a blank line: stdlib → third-party → local. `ruff` enforces this automatically.

```python
# Good
import os
import sys

import pytest

from myproject.utils import format_date

# Bad — mixed groups, no separation
import sys, os
from myproject.utils import format_date
import pytest
```

### Naming Conventions

```python
# Good
MAX_RETRIES = 3

class UserAccount:
    def get_full_name(self, first_name: str, last_name: str) -> str:
        ...

# Bad
maxRetries = 3

class user_account:
    def GetFullName(self, FirstName, LastName):
        ...
```

## Type Annotations

- Add type annotations to **all** function signatures (parameters and return type)
- Use `str | None` union syntax (Python 3.10+) instead of `Optional[str]`
- Annotate module-level constants and class attributes where the type is not obvious
- Use `from __future__ import annotations` at the top of a file only when forward references are needed

```python
# Good
def find_user(user_id: int) -> "User | None":
    ...

def process_items(items: list[str], limit: int = 10) -> dict[str, int]:
    ...

# Bad — missing annotations
def find_user(user_id):
    ...
```

## Docstrings

Every public module, class, method, and function **must** have a docstring. Private helpers (prefixed with `_`) benefit from docstrings when the logic is non-obvious.

### Format

Use the [Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). It is readable as plain text and renders well in editors and documentation tools.

```python
def divide(dividend: float, divisor: float) -> float:
    """Divide two numbers and return the result.

    Args:
        dividend: The number to be divided.
        divisor: The number to divide by. Must not be zero.

    Returns:
        The result of dividing dividend by divisor.

    Raises:
        ValueError: If divisor is zero.

    Example:
        >>> divide(10.0, 2.0)
        5.0
    """
    if divisor == 0:
        raise ValueError("divisor must not be zero")
    return dividend / divisor
```

### Module Docstrings

Every module must begin with a one-line summary followed by a blank line and a longer description when needed:

```python
"""Utility functions for date and time formatting.

Provides helpers for converting between ISO 8601 strings and Python
datetime objects, with consistent timezone handling.
"""
```

### Class Docstrings

Document the class purpose in the class docstring. Document `__init__` parameters there (not in a separate `__init__` docstring) when the class has a public constructor:

```python
class RetryPolicy:
    """Configures retry behaviour for HTTP requests.

    Args:
        max_attempts: Maximum number of attempts before giving up.
        backoff_seconds: Wait time in seconds between attempts.
        exceptions: Tuple of exception types that trigger a retry.

    Example:
        >>> policy = RetryPolicy(max_attempts=3, backoff_seconds=1.0)
        >>> policy.max_attempts
        3
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_seconds: float = 1.0,
        exceptions: tuple[type[Exception], ...] = (OSError,),
    ) -> None:
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.exceptions = exceptions
```

### Docstring Rules

- The first line is a short, imperative-mood summary ending with a period: "Return the user." not "Returns the user" or "This function returns the user."
- Wrap body lines at **99 characters** to match the line length limit
- Do not restate the function signature in the docstring — describe intent, not implementation
- Keep `Args`, `Returns`, `Raises`, and `Example` sections only when they add value; omit empty sections

## Error Handling

- Catch the **most specific** exception type possible — never bare `except:` or `except Exception:` as a catch-all unless re-raising
- Always include a meaningful message when raising an exception
- Prefer raising built-in exceptions (`ValueError`, `TypeError`, `RuntimeError`) before defining custom ones
- Use custom exceptions only when callers need to distinguish them programmatically

```python
# Good
def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"port must be an integer, got {value!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return port

# Bad — swallows errors silently
def parse_port(value):
    try:
        return int(value)
    except:
        return None
```

## Testing with pytest

### File and Function Naming

```
tests/
  unit/
    test_<module>.py
  integration/
    test_<feature>.py
```

- Test files: `test_<module_name>.py`
- Test functions: `test_<what_is_being_tested>_<expected_outcome>()`
- Test classes: `Test<ClassName>` (only group tests when shared fixtures justify it)

### Writing Tests

- Each test function covers **one behaviour** — do not assert multiple unrelated things
- Use `pytest.raises` to assert expected exceptions
- Use `pytest.mark.parametrize` to avoid duplicating test code for similar inputs
- Prefer plain `assert` statements over helper assertion methods

```python
import pytest

from myproject.math_utils import divide


def test_divide_returns_correct_result() -> None:
    assert divide(10.0, 2.0) == 5.0


def test_divide_raises_on_zero_divisor() -> None:
    with pytest.raises(ValueError, match="divisor must not be zero"):
        divide(10.0, 0.0)


@pytest.mark.parametrize(
    ("dividend", "divisor", "expected"),
    [
        (6.0, 2.0, 3.0),
        (-6.0, 2.0, -3.0),
        (0.0, 5.0, 0.0),
    ],
)
def test_divide_parametrized(dividend: float, divisor: float, expected: float) -> None:
    assert divide(dividend, divisor) == expected
```

### Fixtures

Define shared fixtures in `conftest.py` at the appropriate scope. Prefer function-scoped fixtures unless setup is expensive.

```python
# tests/conftest.py
import pytest

from myproject.models import User


@pytest.fixture()
def sample_user() -> User:
    """Return a minimal User instance for testing."""
    return User(id=1, name="Alice", email="alice@example.com")
```

### pytest Configuration

Configure `pytest` in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

## Ruff Configuration

Configure `ruff` in `pyproject.toml`. Enable at minimum the following rule sets:

```toml
[tool.ruff]
line-length = 99
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "D",   # pydocstyle
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "RUF", # ruff-specific rules
]
ignore = [
    "D100", # Missing docstring in public module (use module-level docstrings instead)
    "D104", # Missing docstring in public package
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["<your_package_name>"]
```

## Project Layout

```
<project-root>/
  pyproject.toml       # Project metadata, uv deps, ruff + pytest config
  uv.lock              # Locked dependency versions — always commit this
  src/
    <package_name>/
      __init__.py
      ...
  tests/
    conftest.py
    unit/
    integration/
```

- Use the `src/` layout to prevent accidental imports of the uninstalled package
- Always commit `uv.lock` — it guarantees reproducible environments
- Never commit `.venv/` — add it to `.gitignore`

## General Rules

- **No commented-out code** — delete it; version control preserves history
- **No `print()` in production code** — use the `logging` module
- **No magic numbers** — assign them to named constants with a docstring or inline comment explaining the value
- **Keep functions small** — aim for ≤ 30 lines per function; split when logic can be named clearly
- **Avoid mutable default arguments** — use `None` as default and assign inside the function

```python
# Good
def append_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# Bad — mutable default is shared across all calls
def append_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items
```
