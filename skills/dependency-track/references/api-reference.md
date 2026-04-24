# API Reference and Troubleshooting

## Common API Response Codes

| Code | Meaning | Resolution |
|------|---------|-----------|
| 200 | Success | Operation completed successfully |
| 201 | Created | Resource was created |
| 400 | Bad Request | Invalid request format or missing required fields |
| 401 | Unauthorized | API key is invalid or missing |
| 403 | Forbidden | User doesn't have permission for this operation |
| 404 | Not Found | Resource (project, component) doesn't exist |
| 409 | Conflict | Duplicate or conflicting resource |
| 500 | Internal Error | Server error, check Dependency-Track logs |

## Useful jq Filters

Parse Dependency-Track API responses efficiently:

```bash
# Extract project UUID
jq -r '.uuid'

# Extract all project names
jq '.[] | .name'

# Count components
jq '.components | length'

# Get component names and versions
jq '.components[] | "\(.name):\(.version)"'

# Filter vulnerabilities by severity
jq '.vulnerabilities[] | select(.severity=="CRITICAL")'

# Format vulnerability report
jq '.vulnerabilities[] | {title, severity, cvssScore: .cvssv3, cve}'

# Extract external references
jq '.externalReferences[] | {type, url}'

# Combine multiple filters
jq '.vulnerabilities | map(select(.severity=="CRITICAL" or .severity=="HIGH")) | length'
```

## Debugging Commands

### Check Dependency-Track Server Status

```bash
# Test connectivity
curl -I https://dtrack.example.com/api/v1/project

# Get API version
curl -s https://dtrack.example.com/api/v1/version | jq '.'

# Verify API key by fetching first project
curl -s "https://dtrack.example.com/api/v1/project?limit=1" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.[] | .uuid'
```

### View API Request Details

```bash
# Add verbose output to see headers
curl -v -X POST "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'

# Pretty-print request body
cat << 'EOF' | curl -s -X POST "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @-
{
  "name": "Test Project",
  "version": "1.0.0"
}
EOF
```

### Inspect SBOM Upload

```bash
# Show full response including headers
curl -i -X POST "https://dtrack.example.com/api/v1/bom" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "projectUuid=PROJECT_UUID" \
  -F "bom=@sbom.json" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4"

# Check SBOM processing status
curl -s "https://dtrack.example.com/api/v1/bom/processing?limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'
```

## Troubleshooting Guide

### Issue: "401 Unauthorized"

**Symptoms**: API calls fail with 401 status

**Solutions**:
```bash
# Verify API key is correct
echo "Your API Key: $DTRACK_API_KEY"

# Generate new API key in Dependency-Track UI
# Admin → API Keys → Create New Key

# Check header format
curl -s "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_NEW_API_KEY" | jq '.[] | .uuid' | head -5
```

### Issue: "404 Project Not Found"

**Symptoms**: Project operations fail with 404

**Solutions**:
```bash
# List all projects to find correct UUID
curl -s "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.[] | {uuid, name, version}'

# Search for specific project
curl -s "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" | \
  jq '.[] | select(.name=="Your Project")'

# Verify UUID is correctly formatted (UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
```

### Issue: "SBOM Upload Fails"

**Symptoms**: SBOM upload returns error

**Solutions**:
```bash
# Validate SBOM format (JSON preferred)
jq empty sbom.json        # For JSON files
xmllint --noout sbom.xml  # For XML files

# Check file size (max usually 50MB)
ls -lh sbom.json

# Try with explicit specification version
curl -X POST "https://dtrack.example.com/api/v1/bom" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "projectUuid=PROJECT_UUID" \
  -F "bom=@sbom.json" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4"

# Check processing status
curl -s "https://dtrack.example.com/api/v1/bom/processing" \
  -H "X-API-Key: YOUR_API_KEY" | jq '.[-1]'
```

### Issue: "SBOM Upload Returns 404 Despite Project Existing"

**Symptoms**:
- `POST /api/v1/bom` returns 404 "The project could not be found"
- Project exists (verified via `GET /api/v1/project/{uuid}`)
- Same project UUID works for GET but not for SBOM upload
- Issue may be specific to Dependency-Track v4.14.1

**Diagnostic Commands**:
```bash
# 1. Verify project exists and get full details
curl -s "https://dtrack.example.com/api/v1/project/PROJECT_UUID" \
  -H "X-API-Key: YOUR_API_KEY" | jq '{name, uuid, version, active, isLatest}'

# 2. Attempt SBOM upload with full response headers
curl -i -X POST "https://dtrack.example.com/api/v1/bom" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "projectUuid=PROJECT_UUID" \
  -F "bom=@sbom.json" \
  -F "bomFormat=CycloneDX" \
  -F "bomSpecVersion=1.4" 2>&1 | head -30

# 3. Check SBOM file validity
jq '.components | length' sbom.json    # Should show number > 0
file sbom.json                         # Should show JSON format

# 4. Verify server version
curl -s "https://dtrack.example.com/api/v1/version" \
  -H "X-API-Key: YOUR_API_KEY" | jq '.version'

# 5. Check BOM processing queue (may show pending uploads)
curl -s "https://dtrack.example.com/api/v1/bom/processing?limit=10" \
  -H "X-API-Key: YOUR_API_KEY" | jq '.'
```

**Known Server-Side Bug (v4.14.1)**: The SBOM upload endpoint has a validation bug that prevents uploads to existing projects. This is a server bug, not a client issue.

**Workarounds**:

1. **Use Web UI Instead** (Confirmed Working):
   ```
   Login → Projects → Select Project → Upload SBOM button
   ```

2. **Check Server Logs** for detailed error information:
   ```bash
   # For Docker deployments
   docker logs dependency-track | grep -i "bom\|404" | tail -30

   # For Kubernetes
   kubectl logs -n dependency-track pod/dependency-track-0 | grep -i "bom\|404"

   # For direct installations
   tail -100 /var/log/dependency-track/app.log | grep -i "bom"
   ```

3. **Try Alternative Request Formats**:
   ```bash
   # Ensure multipart form-data (NOT JSON body)
   curl -X POST "https://dtrack.example.com/api/v1/bom" \
     -H "X-API-Key: YOUR_API_KEY" \
     -F "projectUuid=PROJECT_UUID" \
     -F "bom=@sbom.json" \
     -F "bomFormat=CycloneDX"
   ```

4. **Upgrade Server**: Issue may be fixed in v4.15+

5. **Validate Server Configuration**:
   - Ensure all components are running (check health endpoint)
   - Verify database connectivity
   - Check for resource constraints (disk, memory)

### Issue: "Components Not Detected After SBOM Upload"

**Symptoms**: SBOM uploaded but no components appear

**Solutions**:
```bash
# Verify SBOM has components section (JSON format preferred)
jq '.components | length' sbom.json  # JSON format
grep -n "<components>" sbom.xml  # XML format

# Check if components have required metadata
jq '.components | length' sbom.json

# For Java projects, ensure Maven plugin is configured correctly
mvn org.cyclonedx:cyclonedx-maven-plugin:2.7.10:makeAggregateBom -DincludeTransitiveDependencies=true -DoutputFormat=json

# Regenerate SBOM with more verbose output (JSON preferred)
syft packages -o cyclonedx-json -v > sbom.json
```

### Issue: "External Reference Add Fails"

**Symptoms**: Adding external references returns error

**Solutions**:
```bash
# Verify external reference type is valid
# Valid types: VCS, ISSUE_TRACKER, WEBSITE, DOCUMENTATION, SUPPORT, BUILD_SYSTEM, DISTRIBUTION

# Check URL format
curl -X POST "https://dtrack.example.com/api/v1/project/PROJECT_UUID/externalReferences" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "VCS", "url": "https://github.com/owner/repo"}' \
  -v

# List existing external references
curl -s "https://dtrack.example.com/api/v1/project/PROJECT_UUID" \
  -H "Authorization: Bearer YOUR_API_KEY" | \
  jq '.externalReferences'
```

## Performance Optimization

### Batch Operations

```bash
# Create multiple projects efficiently with jq
cat projects.json | jq -r '.projects[] | @json' | while read project; do
  curl -s -X POST "https://dtrack.example.com/api/v1/project" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$project" | jq -r '.uuid'
done
```

### Pagination

```bash
# Fetch all projects with pagination
curl -s "https://dtrack.example.com/api/v1/project?limit=100&offset=0" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.' > page1.json

curl -s "https://dtrack.example.com/api/v1/project?limit=100&offset=100" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.' > page2.json

# Combine results
jq -s '.[0] + .[1]' page1.json page2.json
```

### Caching Results

```bash
# Cache project UUIDs for faster lookups
curl -s "https://dtrack.example.com/api/v1/project" \
  -H "Authorization: Bearer YOUR_API_KEY" | \
  jq '.[] | {name, uuid}' > projects_cache.json

# Lookup from cache
jq '.[] | select(.name=="My Project") | .uuid' projects_cache.json
```

## Monitoring and Health Checks

### Monitor Vulnerability Trends

```bash
#!/bin/bash

PROJECT_UUID="your-project-uuid"

# Get current vulnerability count by severity
echo "=== Vulnerability Summary ==="
curl -s "https://dtrack.example.com/api/v1/project/$PROJECT_UUID/vulnerabilities" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '.vulnerabilities | group_by(.severity) | map({severity: .[0].severity, count: length})'

# Track over time
echo "Severity,Count,Date" > vuln_trend.csv
for day in {0..7}; do
  COUNT=$(curl -s "https://dtrack.example.com/api/v1/project/$PROJECT_UUID/vulnerabilities" \
    -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities | length')
  echo "Total,$COUNT,$(date -d "-$day day" +%Y-%m-%d)" >> vuln_trend.csv
done
```

### Project Health Check

```bash
#!/bin/bash

PROJECT_UUID="your-project-uuid"

echo "=== Project Health Report ==="

# Project info
curl -s "https://dtrack.example.com/api/v1/project/$PROJECT_UUID" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '{name, version, lastBomImportFormat, externalReferencesUrl}'

# Component count
COMPONENTS=$(curl -s "https://dtrack.example.com/api/v1/component?project=$PROJECT_UUID" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.components | length')
echo "Components: $COMPONENTS"

# Vulnerabilities
CRITICAL=$(curl -s "https://dtrack.example.com/api/v1/project/$PROJECT_UUID/vulnerabilities?severity=CRITICAL" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities | length')
echo "Critical Vulnerabilities: $CRITICAL"

# SBOM age
LAST_BOM=$(curl -s "https://dtrack.example.com/api/v1/project/$PROJECT_UUID" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq -r '.lastBomImportDate')
echo "Last SBOM Import: $LAST_BOM"
```

## Integration Examples

### GitLab CI

```yaml
upload_sbom:
  stage: deploy
  script:
    - export SBOM_FILE="sbom-$(date +%Y%m%d).xml"
    - syft packages -o cyclonedx-xml > $SBOM_FILE
    - |
      curl -X POST "$DTRACK_URL/api/v1/bom" \
        -H "Authorization: Bearer $DTRACK_API_KEY" \
        -F "projectUuid=$PROJECT_UUID" \
        -F "bom=@$SBOM_FILE" \
        -F "bomFormat=CycloneDX"
  artifacts:
    paths:
      - $SBOM_FILE
```

### Jenkins Pipeline

```groovy
pipeline {
  stages {
    stage('Upload SBOM') {
      steps {
        script {
          sh '''
            syft packages -o cyclonedx-json > sbom.json
            curl -X POST "${DTRACK_URL}/api/v1/bom" \
              -H "Authorization: Bearer ${DTRACK_API_KEY}" \
              -F "projectUuid=${PROJECT_UUID}" \
              -F "bom=@sbom.json" \
              -F "bomFormat=CycloneDX"
          '''
        }
      }
    }
  }
}
```

## Security Considerations

### API Key Management

```bash
# Never hardcode API keys
# Always use environment variables or secrets management

# For local development, use .env (add to .gitignore)
DTRACK_API_KEY=your-secret-key
export DTRACK_API_KEY

# For CI/CD, use platform secrets
# GitHub Actions: Settings → Secrets and variables → Actions
# GitLab CI: Settings → CI/CD → Variables
# Jenkins: Credentials Store

# Rotate API keys regularly (every 90 days recommended)
# Generate new key and update configurations before deleting old key
```

### HTTPS/TLS Verification

```bash
# Always use HTTPS in production
# Verify SSL certificates
curl --cacert /path/to/ca-bundle.crt "https://dtrack.example.com/api/v1/project"

# For self-signed certificates (development only)
curl -k "https://dtrack.example.com/api/v1/project"  # NOT RECOMMENDED FOR PRODUCTION
```

## Resource Limits

Dependency-Track API typically has these limits:

| Resource | Limit |
|----------|-------|
| SBOM file size | 50 MB |
| API requests | 1000 per minute (varies by configuration) |
| Project name length | 255 characters |
| Description length | 1000 characters |
| Tags per project | Unlimited |
| External references | Unlimited |

Plan accordingly for large SBOM files or high-volume integrations.
