# Dependency-Track Agent Skill

This skill provides comprehensive guidance for integrating with Dependency-Track using the REST API. It enables automated project creation, SBOM management, and dependency tracking workflows.

⚠️ **Important**: See [Known Issues](./SKILL.md#known-issues) for v4.14.1 SBOM upload bug and version compatibility notes.

## Quick Start

### 1. Prerequisites

- Dependency-Track server running and accessible (v4.13+ recommended)
- API key generated in Dependency-Track administration
- SBOM file in CycloneDX or SPDX format (optional for initial setup)
- `curl` and `jq` installed locally

### 2. Basic Setup

Create a `.env` file with your configuration:

```bash
export DTRACK_URL="https://dtrack.your-domain.com"
export DTRACK_API_KEY="your-api-key-from-dtrack"
export DTRACK_VERSION="4.14"  # Set to your Dependency-Track version
```

Load the configuration:
```bash
source .env
```

### 3. Determine Your API Authentication Format

Dependency-Track uses different authentication headers by version:

```bash
# Try modern format (v4.13+)
curl -s "$DTRACK_URL/api/v1/project?limit=1" \
  -H "X-API-Key: $DTRACK_API_KEY" > /dev/null && \
  echo "Using X-API-Key header (modern)" || \
  echo "Using Authorization: Bearer header (legacy)"
```

### 4. Create Your First Project

```bash
# Determine HTTP method based on version
if [[ "$DTRACK_VERSION" > "4.13" ]]; then
  METHOD="PUT"
else
  METHOD="POST"
fi

# Create a parent project
PARENT=$(curl -s -X "$METHOD" "$DTRACK_URL/api/v1/project" \
  -H "X-API-Key: $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Organization",
    "version": "1.0.0"
  }' | jq -r '.uuid')

# Create a child project
PROJECT=$(curl -s -X "$METHOD" "$DTRACK_URL/api/v1/project" \
  -H "X-API-Key: $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Application",
    "parent": {"uuid": "'$PARENT'"},
    "version": "1.0.0"
  }' | jq -r '.uuid')

echo "Project created: $PROJECT"
```

## Skill Documentation

### Core Files

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Main skill documentation with API operations, workflows, and examples |
| [references/templates.md](references/templates.md) | Setup scripts, helper functions, and configuration templates |
| [references/api-reference.md](references/api-reference.md) | API troubleshooting guide, debugging commands, and optimization tips |
| [references/examples.md](references/examples.md) | Real-world use cases and integration patterns |

### Key Sections in SKILL.md

1. **Prerequisites** - Required setup and dependencies
2. **Available Operations** - Complete list of API operations
3. **Authentication** - How to authenticate API calls
4. **Workflow** - Step-by-step process for common tasks
5. **Creating Projects** - Guide to parent and child project creation
6. **Uploading SBOMs** - SBOM format requirements and upload process
7. **External References** - Linking to source code, issue tracking, and documentation
8. **Updating Metadata** - Customizing project information
9. **Complete Workflow Example** - End-to-end microservice onboarding scenario
10. **Best Practices** - Recommended patterns and strategies

## Common Tasks

### Task 1: Onboard a New Project

```bash
# Use helper functions from references/templates.md
source dtrack-helpers.sh

# Create parent
PARENT_ID=$(create_parent_project "Platform Name")

# Create child
PROJECT_ID=$(create_child_project "Service Name" "$PARENT_ID")

# Upload SBOM
upload_sbom "$PROJECT_ID" "./sbom.xml"

# Add references
add_external_reference "$PROJECT_ID" "VCS" "https://github.com/owner/repo"
add_external_reference "$PROJECT_ID" "ISSUE_TRACKER" "https://github.com/owner/repo/issues"
```

### Task 2: Upload SBOM to Existing Project

```bash
curl -X POST "$DTRACK_URL/api/v1/bom" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -F "projectUuid=$PROJECT_UUID" \
  -F "bom=@sbom.xml" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4"
```

### Task 3: Generate SBOM

Use appropriate tool for your language:

```bash
# JavaScript/Node.js
npm install -g @cyclonedx/npm
cyclonedx-npm -o sbom.xml

# Java/Maven
mvn org.cyclonedx:cyclonedx-maven-plugin:2.7.10:makeAggregateBom

# Python
pip-audit --desc --format cyclonedx > sbom.xml

# Any language
syft packages -o cyclonedx-xml > sbom.xml
```

### Task 4: Query Vulnerabilities

```bash
# Get all vulnerabilities
curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID/vulnerabilities" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '.vulnerabilities[] | {title, severity, cve}'

# Get critical vulnerabilities only
curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID/vulnerabilities?severity=CRITICAL" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.'
```

## Workflow Examples

### Multi-Project Setup

For setting up multiple related projects, see [examples.md](references/examples.md):
- **SaaS Applications** - Multi-tenant project organization
- **Microservices** - Service-based architecture tracking
- **Compliance** - Audit trail and compliance reporting
- **Organization-Wide Inventory** - Central dependency tracking

### CI/CD Integration

Ready-to-use configurations for:
- **GitHub Actions** - Automatic SBOM upload on build
- **GitLab CI** - Pipeline integration example
- **Jenkins** - Declarative pipeline setup

See [examples.md](references/examples.md) for complete pipeline examples.

## Troubleshooting

Common issues and solutions are documented in [api-reference.md](references/api-reference.md):

| Problem | Section |
|---------|---------|
| API authentication fails | "Issue: 401 Unauthorized" |
| Project not found | "Issue: 404 Project Not Found" |
| SBOM upload fails | "Issue: SBOM Upload Fails" |
| Components not detected | "Issue: Components Not Detected After SBOM Upload" |
| External references fail | "Issue: External Reference Add Fails" |

## Best Practices

### Project Organization
- Use parent projects for organizational containers
- Create child projects for independently-versioned components
- Tag projects consistently by environment and criticality

### SBOM Management
- Generate SBOMs automatically in CI/CD pipelines
- Update SBOMs regularly with dependency changes
- Validate SBOM format before upload

### External References
- Always link to source code repository (VCS)
- Connect issue tracker for vulnerability traceability
- Add API documentation for discoverability

### Security
- Rotate API keys regularly (90-day intervals recommended)
- Use environment variables or secrets management for API keys
- Never commit credentials to version control

## Integration Checklist

- [ ] Dependency-Track server is accessible
- [ ] API key is generated and stored securely
- [ ] Parent project is created for your organization
- [ ] Child projects are created for each component
- [ ] SBOM generation is configured in build pipeline
- [ ] SBOM upload is automated in CI/CD
- [ ] External references are linked to source/issue/docs
- [ ] Vulnerability monitoring alerts are configured
- [ ] Team has access to Dependency-Track dashboard

## Resources

- **Main Documentation**: [SKILL.md](SKILL.md)
- **Setup Templates**: [references/templates.md](references/templates.md)
- **Troubleshooting**: [references/api-reference.md](references/api-reference.md)
- **Use Case Examples**: [references/examples.md](references/examples.md)
- **Official Docs**: [Dependency-Track REST API](https://docs.dependencytrack.org/integrations/rest-api/)
- **SBOM Formats**: [CycloneDX](https://cyclonedx.org/) | [SPDX](https://spdx.github.io/)

## Support

When working with this skill:

1. **Check the main documentation** in [SKILL.md](SKILL.md) for API operations
2. **Review examples** in [references/examples.md](references/examples.md) for your use case
3. **Consult templates** in [references/templates.md](references/templates.md) for setup scripts
4. **Debug issues** using [references/api-reference.md](references/api-reference.md)
5. **Validate SBOM** files before upload using provided validation scripts

## Next Steps

1. Read [SKILL.md](SKILL.md) for complete API documentation
2. Choose your use case from [references/examples.md](references/examples.md)
3. Use setup scripts from [references/templates.md](references/templates.md)
4. Test your integration and monitor vulnerabilities
5. Integrate with your CI/CD pipeline for automated SBOM uploads
