---
applyTo: "{Dockerfile,docker-compose*.yml,docker-compose*.yaml,.dockerignore}"
---

# Docker Container Strategy and Patterns

All container definitions in this organization must follow these standards. These guidelines apply to `Dockerfile`, `docker-compose*.yml`, and related container configuration files.

## Base Image Selection

- Always pin base images to a specific digest or minor version tag — never use `latest`
- Prefer **Alpine**-based images to minimize attack surface and image size:
  - Python: `python:3.12-alpine3.20`
  - Node.js: `node:20-alpine3.20`
  - Generic: `alpine:3.20`
- For applications requiring glibc (e.g., native extensions), use `slim` Debian variants: `python:3.12-slim-bookworm`
- Scan base images with `docker scout` or Trivy before adopting a new base

```dockerfile
# Good
FROM python:3.12-alpine3.20

# Bad
FROM python:latest
FROM ubuntu:latest
```

## Multi-Stage Builds

Always use multi-stage builds to separate the build environment from the runtime image.

```dockerfile
# Stage 1: builder
FROM python:3.12-alpine3.20 AS builder

WORKDIR /build

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Stage 2: runtime
FROM python:3.12-alpine3.20 AS runtime

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /build/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- The final runtime image must **never** contain build tools, compilers, or test dependencies
- Aim for runtime images under **200 MB**; document any justified exceptions

## Non-Root User

Containers must never run as root in production.

```dockerfile
# Create a dedicated non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set ownership
COPY --chown=appuser:appgroup src/ ./src/

USER appuser
```

- Assign UID/GID explicitly to avoid conflicts with host filesystem permissions (e.g., `adduser -S -u 1001 appuser`)
- The app must not need `sudo` or elevated privileges at runtime

## Layer Optimization

- Order `COPY` and `RUN` instructions from **least frequently changed** (system packages, dependency files) to **most frequently changed** (application source code)
- Group related `RUN` commands with `&&` and `\` to reduce layers
- Clean up package manager caches in the same `RUN` step:

```dockerfile
RUN apk add --no-cache \
    curl \
    postgresql-libs \
 && pip install uv \
 && uv sync --frozen --no-dev \
 && pip uninstall -y uv
```

- Use `.dockerignore` to exclude files not needed in the image:

```dockerignore
.git
.github
.env
.env.*
!.env.sample
__pycache__
*.pyc
*.pyo
*.pyd
tests/
docs/
*.md
.pytest_cache
.mypy_cache
.ruff_cache
node_modules/
dist/
```

## Health Checks

All services that expose a port must declare a `HEALTHCHECK`.

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1
```

- The health endpoint (`/health` or `/healthz`) must be lightweight — no database calls
- Use `--start-period` to give the container time to initialize before health checks begin

## Environment Variables and Secrets

- Use `ENV` only for non-sensitive runtime configuration (e.g., `PORT`, `LOG_LEVEL`)
- **Never** bake secrets into images using `ENV`, `ARG`, or `COPY`
- Pass secrets at runtime via orchestrator secret management (Docker Swarm secrets, Kubernetes secrets, or environment injection)
- Document all required environment variables in a `README` or `.env.sample` next to the `Dockerfile`

```dockerfile
# Good — non-secret defaults
ENV PORT=8000 \
    LOG_LEVEL=info \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Bad — never do this
ENV DATABASE_PASSWORD=supersecret
```

## Docker Compose Patterns

Use Docker Compose for local development and integration testing.

```yaml
version: "3.9"

services:
  app:
    build:
      context: .
      target: runtime
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

- Always define `healthcheck` on stateful services (databases, message brokers)
- Use `depends_on` with `condition: service_healthy` — not bare `depends_on`
- Use named volumes for persistent data; never mount the host filesystem for database data in production-like environments
- Use `restart: unless-stopped` for services that should be resilient

## Image Tagging and Versioning

- Tag images with both the Git SHA and the semantic version:
  - `myorg/myapp:1.2.3`
  - `myorg/myapp:sha-abc1234`
  - `myorg/myapp:latest` (only on the default registry for latest stable)
- Build image tags in CI using the Git tag or commit SHA — never build untagged images for deployment
- Retain at least the last 5 release tags in the registry; prune older development/SHA tags

## Security Scanning

- All images must pass a Trivy or Snyk container scan before deployment
- **CRITICAL** and **HIGH** severity CVEs block deployment unless a documented exception is approved
- Rebuild and redeploy images when base images receive security patches — use Renovate or Dependabot to track base image updates
- Never publish images with known secrets or credentials embedded

## Resource Limits

Define resource limits for all services in production-grade Compose files:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.00"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
```
