---
name: dependency-track
description: 'Manage Dependency-Track projects, SBOMs, and component metadata using REST API and CLI tools. Use this skill when users want to create parent/project organizations, upload SBOM files (CycloneDX/SPDX), create external references to source code repositories, configure issue tracking links, add project metadata (description, version, tags), configure notifications, or query component vulnerabilities. Triggers on requests like "create a dependency track parent", "upload SBOM to dependency track", "add source code reference", "link issue tracker to dependency track", "scan for vulnerabilities", "add project metadata", or any Dependency-Track project/SBOM management task.'
---

# Dependency-Track

Manage Dependency-Track projects, SBOMs, and component metadata using the Dependency-Track REST API.

## Prerequisites

- Dependency-Track server running (typically at `https://dtrack.example.com`)
- API key from Dependency-Track (generated in Administration → API Keys)
- SBOM file in CycloneDX or SPDX format
- `curl` or `jq` for API calls
- Basic authentication headers (API key as Bearer token)

## Available Operations

### Core Operations

| Operation | Purpose | Endpoint |
|-----------|---------|----------|
| Create Parent Project | Create a top-level organization/parent project | `POST /api/v1/project` |
| Create Child Project | Create sub-projects under parent | `POST /api/v1/project` (with parent reference) |
| Upload SBOM | Upload CycloneDX/SPDX SBOM to a project | `POST /api/v1/bom` |
| Create External Reference | Link to source code, issue tracker, documentation | `POST /api/v1/project/{id}/externalReferences` |
| Update Project Metadata | Add description, version, tags, contact info | `PATCH /api/v1/project/{id}` |
| Get Project Details | Retrieve project info, components, vulnerabilities | `GET /api/v1/project/{id}` |
| List Components | View all components in a project | `GET /api/v1/component?project={id}` |
| Get Vulnerabilities | Query findings for a project | `GET /api/v1/project/{id}/vulnerabilities` |

## Authentication

### API Key Format

Dependency-Track supports two authentication formats depending on server version:

**Modern Format (v4.13+)** - Recommended:
```bash
-H "X-API-Key: YOUR_API_KEY"
-H "Content-Type: application/json"
```

**Legacy Format (v4.12 and earlier)**:
```bash
-H "Authorization: Bearer YOUR_API_KEY"
-H "Content-Type: application/json"
```

**For SBOM Multipart Uploads**:
```bash
-H "X-API-Key: YOUR_API_KEY"
# Content-Type is set automatically by curl for multipart/form-data
```

### Determining Your Server Version

```bash
echo "Your API Format:"
curl -s "https://dtrack.example.com/api/v1/project?limit=1" \
  -H "X-API-Key: YOUR_API_KEY" > /dev/null && echo "X-API-Key format (modern)" || \
  curl -s "https://dtrack.example.com/api/v1/project?limit=1" \
  -H "Authorization: Bearer YOUR_API_KEY" > /dev/null && echo "Bearer format (legacy)"
```

## Workflow

1. **Create parent project**: Establish organization/parent for all related projects
2. **Create child projects**: Add sub-projects (one per deliverable/component)
3. **Generate/obtain SBOM**: Ensure CycloneDX 1.4+ or SPDX 2.2+ format
4. **Upload SBOM**: Associate SBOM with the child project
5. **Add external references**: Link to source code repo, issue tracker, documentation
6. **Configure metadata**: Add description, version, tags, contact information
7. **Monitor vulnerabilities**: Review and track component findings

## Creating Projects

### Step 1: Create Parent Project

Parent projects (without parent_uuid) serve as organizational containers:

```bash
curl -X PUT "https://dtrack.example.com/api/v1/project" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Parent Organization Name",
    "description": "Parent project for organizing related deliverables",
    "version": "1.0.0",
    "tags": ["parent", "organization"]
  }' | jq '.'
```

**Response** includes:
- `uuid`: Project UUID (needed for SBOM upload and external references)
- `name`, `description`, `version`
- `created`, `lastBomImportFormat` (initially null)

**Note on HTTP Method**: Dependency-Track v4.14+ uses **PUT** instead of POST for project creation:

```bash
# For v4.14+
curl -X PUT "https://dtrack.example.com/api/v1/project" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '...'

# For v4.13 and earlier
curl -X POST "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '...'
```

**Step 2: Create Child Projects**

Create projects under the parent (requires parent_uuid):

```bash
curl -X PUT "https://dtrack.example.com/api/v1/project" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Child Project Name",
    "description": "Description of this specific project/component",
    "version": "1.0.0",
    "parent": {
      "uuid": "PARENT_UUID_FROM_STEP_1"
    },
    "tags": ["production", "critical"]
  }' | jq '.'
```

**Best Practices**:
- Use meaningful names reflecting the deliverable (e.g., "Backend API", "Mobile App", "CLI Tool")
- Include version numbers for tracking releases
- Tag projects by environment (production, staging, development) or category (critical, optional)
- Parent projects can have multiple children

## Uploading SBOMs

### Prerequisites

- Valid CycloneDX (1.3, 1.4, 1.5) or SPDX (2.1, 2.2, 2.3) SBOM file
- Project UUID created in previous step
- SBOM in JSON format (preferred) or XML format

### Upload Process

```bash
curl -X POST "https://dtrack.example.com/api/v1/bom" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "projectUuid=PROJECT_UUID" \
  -F "bom=@/path/to/sbom.json" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4"
```

⚠️ **Known Issue (v4.14.1)**: See [Known Issues](#known-issues) section below for SBOM upload failures.

**Parameters**:
- `projectUuid`: Target project UUID (required)
- `bom`: SBOM file path (required)
- `bomFormat`: "CycloneDX" or "SPDX" (required)
- `bomSpecVersion`: Format version (e.g., "1.4" for CycloneDX, "2.2" for SPDX) (optional, auto-detected)

**Response**:
```json
{
  "project": {"uuid": "PROJECT_UUID"},
  "bom": {
    "uuid": "BOM_UUID",
    "generation_timestamp": "2024-04-24T12:00:00Z",
    "component_count": 42
  }
}
```

### Generating SBOMs

If you don't have an SBOM, generate one using tools (JSON format preferred):

| Tool | Language | Command |
|------|----------|---------|
| **Syft** | Multi-language | `syft packages -o cyclonedx-json > sbom.json` |
| **npm** | JavaScript | `npm install -g @cyclonedx/npm && cyclonedx-npm -o sbom.json -oF json` |
| **pip-audit** | Python | `pip-audit --desc --format cyclonedx --output sbom.json` |
| **Poetry** | Python | `poetry export --format=sbom --output=sbom.json` |
| **CycloneDX Maven** | Java/Maven | `mvn org.cyclonedx:cyclonedx-maven-plugin:2.7.10:makeAggregateBom -DoutputFormat=json` |
| **CycloneDX Gradle** | Java/Gradle | `gradle cycloneDxBom -PcycloneDxBom_format=json` |
| **FOSSA** | Multi-language | `fossa generate-lockfile && fossa analyze --format json` |

## Creating External References

External references link projects to related resources (source code, issue trackers, documentation).

### Reference Types

| Type | Purpose | Example URL |
|------|---------|-------------|
| `VCS` | Version Control System | `https://github.com/owner/repo` |
| `ISSUE_TRACKER` | Issue/Bug Tracking | `https://github.com/owner/repo/issues` |
| `WEBSITE` | Project Website | `https://project.example.com` |
| `DOCUMENTATION` | API/Developer Docs | `https://docs.example.com` |
| `SUPPORT` | Support/Help | `https://support.example.com` |
| `BUILD_SYSTEM` | CI/CD Pipeline | `https://github.com/owner/repo/actions` |
| `DISTRIBUTION` | Package Registry/Repo | `https://registry.npmjs.org/package` |

### Add External References

```bash
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "VCS",
    "url": "https://github.com/owner/repo-name"
  }' | jq '.'
```

### Add Multiple References

```bash
# Source Code Repository
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "VCS", "url": "https://github.com/owner/backend-api"}'

# Issue Tracker
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "ISSUE_TRACKER", "url": "https://github.com/owner/backend-api/issues"}'

# Documentation
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "DOCUMENTATION", "url": "https://api.example.com/docs"}'

# CI/CD Pipeline
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "BUILD_SYSTEM", "url": "https://github.com/owner/backend-api/actions"}'
```

## Updating Project Metadata

Update project details after creation:

```bash
curl -X PATCH "https://dtrack.example.com/api/v1/project/PROJECT_UUID" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Complete description of the project",
    "version": "2.0.1",
    "tags": ["critical", "production", "api"],
    "group": "backend-services",
    "manufacturer": "Your Organization",
    "purl": "pkg:npm/package-name@1.0.0"
  }' | jq '.'
```

**Available Fields**:
- `name`: Project name
- `description`: Detailed project description
- `version`: Project/product version
- `tags`: Array of tags for categorization
- `group`: Organizational grouping
- `manufacturer`: Organization/team name
- `purl`: Package URL (standardized reference format)
- `classifier`: Project classification (application, library, framework, etc.)

## Querying Projects

### Get Project Details

```bash
curl -X GET "https://dtrack.example.com/api/v1/project/PROJECT_UUID" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'
```

**Returns**:
- Project metadata (name, version, description, tags)
- `lastBomImportFormat`: Format of most recent SBOM
- `bom`: Latest SBOM information
- `purl`: Package URL

### List Components in Project

```bash
curl -X GET "https://dtrack.example.com/api/v1/component?project=PROJECT_UUID" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.components[] | {name, version, purl, license}'
```

**Returns**: All dependencies discovered from the uploaded SBOM.

### Get Vulnerabilities

```bash
curl -X GET "https://dtrack.example.com/api/v1/project/PROJECT_UUID/vulnerabilities" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.vulnerabilities[] | {title, severity, cve, status}'
```

**Filter by Severity**:
```bash
curl -X GET "https://dtrack.example.com/api/v1/project/PROJECT_UUID/vulnerabilities?severity=CRITICAL" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'
```

**Severity Levels**: CRITICAL, HIGH, MEDIUM, LOW, INFO, UNASSIGNED

## Complete Workflow Example

### Scenario: Onboard New Microservice

**User**: "Create a dependency track setup for our backend microservices"

**Steps**:

**1. Create Parent Project**
```bash
curl -s -X PUT "https://dtrack.example.com/api/v1/project" \
  -H "X-API-Key: $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backend Microservices",
    "description": "Parent project for all backend services",
    "version": "1.0.0",
    "tags": ["production", "microservices"]
  }' | jq -r '.uuid')

echo "Parent Project UUID: $PARENT_UUID"
```

**2. Create Child Projects** (repeat for each service)
```bash
SERVICE_UUID=$(curl -s -X POST "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Service",
    "description": "Authentication and user management microservice",
    "version": "2.1.0",
    "parent": {"uuid": "'$PARENT_UUID'"},
    "tags": ["critical", "production"]
  }' | jq -r '.uuid')

echo "Service Project UUID: $SERVICE_UUID"
```

**3. Generate and Upload SBOM**
```bash
# Generate SBOM in JSON format (preferred)
syft packages -o cyclonedx-json > user-service-sbom.json

# Upload to Dependency-Track
curl -X POST "https://dtrack.example.com/api/v1/bom" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -F "projectUuid=$SERVICE_UUID" \
  -F "bom=@user-service-sbom.json" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4"
```

**4. Add External References**
```bash
# GitHub Repository
curl -X POST "https://dtrack.example.com/api/v1/project/$SERVICE_UUID/externalReferences" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "VCS", "url": "https://github.com/company/user-service"}'

# Issue Tracker
curl -X POST "https://dtrack.example.com/api/v1/project/$SERVICE_UUID/externalReferences" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "ISSUE_TRACKER", "url": "https://github.com/company/user-service/issues"}'

# API Documentation
curl -X POST "https://dtrack.example.com/api/v1/project/$SERVICE_UUID/externalReferences" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "DOCUMENTATION", "url": "https://docs.company.com/user-service"}'
```

**5. Update Project Metadata**
```bash
curl -X PATCH "https://dtrack.example.com/api/v1/project/$SERVICE_UUID" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Core authentication and user management service. Handles OAuth2, JWT tokens, and user profiles.",
    "group": "microservices",
    "manufacturer": "Engineering Team",
    "tags": ["critical", "production", "java", "api"]
  }'
```

**6. Monitor Vulnerabilities**
```bash
# Get vulnerability summary
curl -X GET "https://dtrack.example.com/api/v1/project/$SERVICE_UUID/vulnerabilities" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities | length'

# Get critical vulnerabilities
curl -X GET "https://dtrack.example.com/api/v1/project/$SERVICE_UUID/vulnerabilities?severity=CRITICAL" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities[] | {title, component, cve}'
```

## Best Practices

### Project Organization

- **Use parent projects** to group related deliverables (microservices, products, releases)
- **Create child projects** for each independently-versioned component
- **Tag consistently** (environment: production/staging/dev, type: api/library/app, owner: team name)

### SBOM Management

- **Update SBOMs regularly** (at each release, security patch, dependency update)
- **Use tools to generate SBOMs** automatically in CI/CD pipeline
- **Validate SBOM format** before upload (use CycloneDX validator)
- **Include all dependencies** transitive and direct (use full dependency tree)

### External References

- **Link to VCS**: Always include source code repository reference
- **Link issue tracker**: Enable traceability from vulnerabilities to fixes
- **Add documentation**: Help teams understand project scope and dependencies
- **Use CI/CD links**: Connect to automation pipelines for visibility

### Metadata

- **Use meaningful descriptions**: Help teams understand project purpose and scope
- **Update version numbers**: Align with project releases
- **Tag appropriately**: Use tags for environment, criticality, technology stack
- **Set manufacturer/group**: Organize by team and organizational unit

## Known Issues

### ⚠️ Dependency-Track v4.14.1 - SBOM Upload Returns 404

**Issue**: SBOM upload (POST /api/v1/bom) returns HTTP 404 "The project could not be found" even when the project exists and can be retrieved via GET requests.

**Symptoms**:
- Project creation succeeds (PUT /api/v1/project returns 201)
- Project retrieval succeeds (GET /api/v1/project/{uuid} returns 200)
- SBOM upload fails (POST /api/v1/bom returns 404)
- Same project UUID works for GET but fails for SBOM upload
- Error message: "The project could not be found."

**Root Cause**: Server-side validation bug in v4.14.1's SBOM upload endpoint

**Tested Workarounds** (all unsuccessful):
- ❌ Using query parameter instead of form field: `POST /api/v1/bom?projectUuid={uuid}`
- ❌ Changing HTTP method to PUT: Returns 415 (Unsupported Media Type)
- ❌ Sending SBOM as JSON body with base64 encoding
- ❌ Alternative endpoint paths: `/api/v1/bom/upload`, `/api/v1/project/{uuid}/bom`, `/api/v1/bom/import`
- ❌ Different request formats (JSON vs multipart/form-data)

**Recommended Solutions**:
1. **Upgrade Dependency-Track** to latest stable version (4.15+) - Issue may be fixed
2. **Use Web UI** for SBOM uploads instead of API (confirmed working)
3. **Check Server Logs** for detailed error messages:
   ```bash
   # Access container logs (if running in Docker)
   docker logs dependency-track | grep -i "bom\|404" | tail -20
   ```
4. **Verify Server Configuration**: Ensure all required components are properly initialized
5. **Test with Different Projects**: Try uploading to multiple projects to isolate issue

**Example: Using Web UI Workaround**:
1. Log in to Dependency-Track web console
2. Navigate to Projects → Select Project
3. Click "Upload SBOM" button
4. Select your CycloneDX JSON or XML file
5. Click "Upload"

**Status**: This issue is server-side and beyond client API control. Awaiting Dependency-Track v4.15+ fix or server logs analysis.

### Older Version Compatibility

**Dependency-Track v4.13 and Earlier**:
- Uses `Authorization: Bearer` header format instead of `X-API-Key`
- Uses POST for project creation instead of PUT
- May have different endpoint paths for newer features

**Version Detection**:
```bash
# Get server version and adjust commands accordingly
curl -s "https://dtrack.example.com/api/v1/version" | jq '.version'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Verify API key is correct; generate new key in Administration → API Keys |
| "Project not found" | Check project UUID is correct; list projects via `GET /api/v1/project` |
| "SBOM format error" | Validate SBOM format (CycloneDX vs SPDX); check specification version matches |
| "External reference failed" | Verify reference type is valid (VCS, ISSUE_TRACKER, etc.); check URL format |
| "Components not detected" | Ensure SBOM includes component metadata; regenerate SBOM with proper tool |
| "SBOM upload returns 404" | See Known Issues section above; may be v4.14.1 server bug |

## References

- [Dependency-Track REST API Docs](https://docs.dependencytrack.org/integrations/rest-api/)
- [CycloneDX Format Specification](https://cyclonedx.org/specification/)
- [SPDX Format Specification](https://spdx.github.io/spdx-spec/)
- [Syft SBOM Generation Tool](https://github.com/anchore/syft)
