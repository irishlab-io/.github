---
applyTo: "**/*.py"
---

# Python Web Application Development Best Practices

All Python web application code in this organization must follow these standards. These guidelines apply to any Python file (`*.py`) across all repositories.

## Code Style and Formatting

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all code
- Use [Ruff](https://docs.astral.sh/ruff/) as the primary linter and formatter — it replaces flake8, isort, and black
- Maximum line length: **99 characters**
- Use **4 spaces** for indentation — never tabs
- Organize imports in three groups separated by blank lines: stdlib → third-party → local

## Type Annotations

- Use type annotations on all function signatures (parameters and return types)
- Use `from __future__ import annotations` for forward references when needed
- Prefer `str | None` over `Optional[str]` (Python 3.10+ union syntax)
- Use `TypeAlias`, `TypeVar`, and `Protocol` from `typing` for reusable types
- Run `mypy` in strict mode on all new code

```python
# Good
def get_user(user_id: int) -> User | None:
    ...

# Bad
def get_user(user_id):
    ...
```

## Project Structure

Follow the [twelve-factor app](https://12factor.net/) methodology:

```
src/
  <app_name>/
    __init__.py
    models.py        # Data models
    views.py         # Route handlers / view functions
    services.py      # Business logic (no HTTP concerns)
    repositories.py  # Data access layer
    schemas.py       # Serialization/validation schemas
    config.py        # Settings loaded from environment
tests/
  unit/
  integration/
  e2e/
```

- Keep **business logic in services**, not in views/routes
- Views should only handle HTTP concerns: parse request, call service, return response
- Never import from `views` in `models` or `services` (dependency direction: views → services → models)

## Dependency Management

- Use [uv](https://docs.astral.sh/uv/) for all dependency management — not pip directly
- Pin all dependencies: `uv add <package>` records exact versions in `uv.lock`
- Separate dev/test dependencies: `uv add --dev pytest ruff mypy`
- Never commit `requirements.txt` generated from pip freeze; use `pyproject.toml` + `uv.lock`

## Configuration and Secrets

- All configuration comes from **environment variables** — never hardcode values
- Use [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for typed, validated settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"
```

- Provide a `.env.sample` file with all required variable names and descriptions (no real values)
- Never log secrets, tokens, or passwords — even at DEBUG level

## Database and ORM

- Use [SQLAlchemy](https://www.sqlalchemy.org/) with the async engine for new projects
- Define all models with explicit column types and constraints
- Always write database migrations with [Alembic](https://alembic.sqlalchemy.org/)
- Migrations must be reversible (include both `upgrade()` and `downgrade()`)
- Never call `Base.metadata.create_all()` in production code

## API Design (REST)

- Use [FastAPI](https://fastapi.tiangolo.com/) for new REST APIs
- Define Pydantic schemas for all request bodies and response models
- Return appropriate HTTP status codes: `201` for creation, `204` for no-content deletes, `422` for validation errors
- Use path parameters for resource identity, query parameters for filtering/pagination
- Version all APIs with a URL prefix: `/api/v1/`
- Document all endpoints with docstrings; FastAPI generates OpenAPI automatically

## Error Handling

- Define custom exception classes for domain errors; never raise bare `Exception`
- Use exception handlers at the app level to map domain exceptions to HTTP responses
- Return structured error responses:

```json
{
  "error": "resource_not_found",
  "message": "User with id 42 does not exist",
  "details": {}
}
```

- Log exceptions with `logger.exception()` to capture the full traceback
- Never swallow exceptions silently with a bare `except: pass`

## Security

- Validate and sanitize **all** user input — never trust data from requests
- Use parameterized queries; never use string formatting for SQL
- Hash passwords with `bcrypt` or `argon2` — never MD5/SHA1
- Set `HttpOnly`, `Secure`, and `SameSite=Strict` on session cookies
- Apply rate limiting on authentication endpoints
- Keep dependencies up to date; run `uv audit` regularly

## Testing

- Use [pytest](https://pytest.org/) with `pytest-cov` for all tests
- Aim for **80%+ line coverage** on business logic (`services.py`, `models.py`)
- Structure tests to mirror source: `tests/unit/test_services.py` mirrors `src/app/services.py`
- Use `pytest-mock` for mocking; avoid patching internals — mock at boundaries
- Write at least one integration test per API endpoint using `httpx.AsyncClient`

```python
async def test_create_user(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/users",
        json={"email": "alice@example.com", "password": "s3cr3t"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
```

## Logging

- Use the stdlib `logging` module; configure with `structlog` for structured output
- Always use a named logger: `logger = logging.getLogger(__name__)`
- Log at the appropriate level: DEBUG for internal state, INFO for normal events, WARNING for recoverable issues, ERROR for failures
- Include correlation IDs in log context for request tracing

## Performance

- Use `async`/`await` for all I/O-bound operations (database queries, HTTP calls, file I/O)
- Cache expensive computations with Redis via `aiocache` or similar
- Profile before optimizing — use `py-spy` or `cProfile` to identify real bottlenecks
- Paginate all list endpoints — never return unbounded result sets
