# Real-World Examples and Use Cases

⚠️ **Important**: See [Known Issues](../SKILL.md#known-issues) in the main SKILL.md for v4.14.1 SBOM upload bug information.

## Use Case 1: Multi-Tenant SaaS Application

**Scenario**: Onboard multiple customer projects with separate SBOMs and tracking

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"

# Detect API format for authentication
if curl -s "$DTRACK_URL/api/v1/project?limit=1" -H "X-API-Key: $DTRACK_API_KEY" > /dev/null 2>&1; then
  AUTH_HEADER="X-API-Key: $DTRACK_API_KEY"
else
  AUTH_HEADER="Authorization: Bearer $DTRACK_API_KEY"
fi

# Create parent project for the SaaS product
PARENT=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SaaS Platform",
    "description": "Parent project for all customer instances",
    "version": "2.0.0",
    "tags": ["platform", "saas", "multi-tenant"]
  }' | jq -r '.uuid')

echo "Parent Project: $PARENT"

# Create child projects for each customer
for customer in customer-a customer-b customer-c; do
  # Create project
  PROJECT=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "'$customer'",
      "description": "Customer instance of SaaS Platform",
      "version": "2.0.0",
      "parent": {"uuid": "'$PARENT'"},
      "tags": ["customer", "'$customer'"]
    }' | jq -r '.uuid')

  echo "Created project for $customer: $PROJECT"

  # Upload SBOM if it exists
  if [ -f "sboms/$customer-sbom.json" ]; then
    echo "Uploading SBOM for $customer..."
    HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "$DTRACK_URL/api/v1/bom" \
      -H "$AUTH_HEADER" \
      -F "projectUuid=$PROJECT" \
      -F "bom=@sboms/$customer-sbom.json" \
      -F "bomFormat=CycloneDX" \
      -o /dev/null)

    if [ "$HTTP_CODE" = "404" ]; then
      echo "⚠️  SBOM upload returned 404 - see Known Issues"
      echo "Workaround: Use web UI to upload SBOM"
    else
      echo "✓ Uploaded SBOM for $customer (HTTP $HTTP_CODE)"
    fi
  fi

  # Add external references
  curl -s -X POST "$DTRACK_URL/api/v1/project/$PROJECT/externalReferences" \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    -d '{"type": "ISSUE_TRACKER", "url": "https://jira.company.com/browse/'$(echo $customer | tr '[:lower:]' '[:upper:]')'"}'
done
```

## Use Case 2: Microservices Architecture

**Scenario**: Track dependencies across interconnected microservices

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"
GITHUB_ORG="company"

# Create parent project
PARENT=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Microservices Platform",
    "description": "Parent project for all microservices",
    "version": "1.0.0",
    "manufacturer": "Platform Team",
    "tags": ["microservices", "production"]
  }' | jq -r '.uuid')

# Services to register
services=(
  "auth-service:8080"
  "user-service:8081"
  "order-service:8082"
  "payment-service:8083"
  "notification-service:8084"
)

for service_info in "${services[@]}"; do
  service=$(echo $service_info | cut -d: -f1)
  port=$(echo $service_info | cut -d: -f2)

  # Create service project
  SERVICE_UUID=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "'$service'",
      "description": "Microservice handling specific business logic",
      "version": "1.2.0",
      "parent": {"uuid": "'$PARENT'"},
      "classifier": "application",
      "tags": ["microservice", "production", "critical"]
    }' | jq -r '.uuid')

  echo "Created $service: $SERVICE_UUID"

  # Add GitHub repository reference
  curl -s -X POST "$DTRACK_URL/api/v1/project/$SERVICE_UUID/externalReferences" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"type": "VCS", "url": "https://github.com/'$GITHUB_ORG'/'$service'"}' > /dev/null

  # Add issue tracker
  curl -s -X POST "$DTRACK_URL/api/v1/project/$SERVICE_UUID/externalReferences" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"type": "ISSUE_TRACKER", "url": "https://github.com/'$GITHUB_ORG'/'$service'/issues"}' > /dev/null

  # Add API documentation
  curl -s -X POST "$DTRACK_URL/api/v1/project/$SERVICE_UUID/externalReferences" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"type": "DOCUMENTATION", "url": "https://docs.company.com/'$service'"}' > /dev/null

  # Generate and upload SBOM
  if [ -d "services/$service" ]; then
    cd "services/$service"
    syft packages -o cyclonedx-json > sbom.json

    curl -s -X POST "$DTRACK_URL/api/v1/bom" \
      -H "Authorization: Bearer $DTRACK_API_KEY" \
      -F "projectUuid=$SERVICE_UUID" \
      -F "bom=@sbom.json" \
      -F "bomFormat=CycloneDX" > /dev/null

    cd - > /dev/null
    echo "Uploaded SBOM for $service"
  fi
done

echo "Microservices setup complete: $PARENT"
```

## Use Case 3: Compliance and Audit Trail

**Scenario**: Maintain detailed metadata for compliance reporting

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"

# Create compliance-tracked project
PROJECT_UUID=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Application",
    "description": "SOC2, HIPAA, GDPR compliant application",
    "version": "3.2.1",
    "manufacturer": "Security Team",
    "group": "Production",
    "classifier": "application",
    "tags": ["soc2", "hipaa", "gdpr", "pci-dss"]
  }' | jq -r '.uuid')

echo "Created compliance project: $PROJECT_UUID"

# Add multiple external references for audit trail
references=(
  "VCS|https://github.com/company/app"
  "DOCUMENTATION|https://docs.compliance.company.com"
  "ISSUE_TRACKER|https://jira.company.com/browse/APP"
  "BUILD_SYSTEM|https://jenkins.company.com/job/app-build"
  "SUPPORT|https://support.company.com"
)

for ref in "${references[@]}"; do
  type=$(echo $ref | cut -d| -f1)
  url=$(echo $ref | cut -d| -f2)

  curl -s -X POST "$DTRACK_URL/api/v1/project/$PROJECT_UUID/externalReferences" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"type": "'$type'", "url": "'$url'"}' > /dev/null

  echo "Added $type reference"
done

# Upload SBOM
curl -X POST "$DTRACK_URL/api/v1/bom" \
  -H "Authorization: Bearer $DTRACK_API_KEY" \
  -F "projectUuid=$PROJECT_UUID" \
  -F "bom=@sbom-compliance.json" \
  -F "bomFormat=CycloneDX"

echo "SBOM uploaded for compliance tracking"

# Generate compliance report
echo "=== Compliance Report ==="
curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '{
    name,
    version,
    manufacturer,
    tags,
    externalReferences: (.externalReferences | map({type, url})),
    lastBomImportDate,
    lastBomImportFormat
  }'
```

## Use Case 4: CI/CD Pipeline Integration

**Scenario**: Automatically upload SBOMs on each build

### GitHub Actions Example

```yaml
name: Build and Upload SBOM

on:
  push:
    branches: [main, develop]
  release:
    types: [published]

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Generate SBOM
        run: |
          npm install -g @cyclonedx/npm
          cyclonedx-npm -o sbom.json -oF json

      - name: Upload to Dependency-Track
        env:
          DTRACK_URL: ${{ secrets.DTRACK_URL }}
          DTRACK_API_KEY: ${{ secrets.DTRACK_API_KEY }}
          PROJECT_UUID: ${{ secrets.PROJECT_UUID }}
        run: |
          curl -X POST "$DTRACK_URL/api/v1/bom" \
            -H "Authorization: Bearer $DTRACK_API_KEY" \
            -F "projectUuid=$PROJECT_UUID" \
            -F "bom=@sbom.json" \
            -F "bomFormat=CycloneDX" \
            -F "bomSpecVersion=1.4"

      - name: Archive SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json
```

### GitLab CI Example

```yaml
stages:
  - build
  - scan
  - upload

build:
  stage: build
  image: node:18
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

generate_sbom:
  stage: scan
  image: node:18
  script:
    - npm install -g @cyclonedx/npm
    - cyclonedx-npm -o sbom.json -oF json
  artifacts:
    paths:
      - sbom.json

upload_sbom:
  stage: upload
  image: curlimages/curl:latest
  script:
    - |
      curl -X POST "$DTRACK_URL/api/v1/bom" \
        -H "Authorization: Bearer $DTRACK_API_KEY" \
        -F "projectUuid=$PROJECT_UUID" \
        -F "bom=@sbom.json" \
        -F "bomFormat=CycloneDX"
  dependencies:
    - generate_sbom
```

## Use Case 5: Vulnerability Response Workflow

**Scenario**: Monitor vulnerabilities and create issues automatically

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"
GITHUB_TOKEN="github-token"
GITHUB_REPO="company/app"

PROJECT_UUID="your-project-uuid"

# Get critical vulnerabilities
VULNS=$(curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID/vulnerabilities?severity=CRITICAL" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities[]')

echo "Processing critical vulnerabilities..."

echo "$VULNS" | while read -r vuln; do
  TITLE=$(echo "$vuln" | jq -r '.title')
  DESCRIPTION=$(echo "$vuln" | jq -r '.description // .title')
  CVE=$(echo "$vuln" | jq -r '.cve // "N/A"')
  COMPONENT=$(echo "$vuln" | jq -r '.components[0].name // "Unknown"')
  SEVERITY=$(echo "$vuln" | jq -r '.severity')

  # Create GitHub issue
  ISSUE=$(curl -s -X POST "https://api.github.com/repos/$GITHUB_REPO/issues" \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Security: '$SEVERITY' vulnerability in '$COMPONENT'",
      "body": "**CVE**: '$CVE'\n\n**Title**: '$TITLE'\n\n**Description**: '$DESCRIPTION'\n\n**Severity**: '$SEVERITY'\n\nSource: Dependency-Track",
      "labels": ["security", "critical", "dependency"],
      "assignees": ["security-team"]
    }' | jq -r '.number')

  echo "Created issue #$ISSUE for vulnerability: $TITLE"
done

echo "Vulnerability response workflow complete"
```

## Use Case 6: Organization-Wide Dependency Inventory

**Scenario**: Maintain central inventory of all projects and dependencies

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"

# Export all projects
echo "Organization,Project,Version,Components,Vulnerabilities,CriticalVulns,LastUpdated" > inventory.csv

curl -s "$DTRACK_URL/api/v1/project?limit=500" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '.[] | select(.parent != null)' | \
  while read -r project; do
    PROJECT_UUID=$(echo "$project" | jq -r '.uuid')
    PROJECT_NAME=$(echo "$project" | jq -r '.name')
    PROJECT_VERSION=$(echo "$project" | jq -r '.version')

    # Get component count
    COMPONENTS=$(curl -s "$DTRACK_URL/api/v1/component?project=$PROJECT_UUID" \
      -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.components | length')

    # Get vulnerability counts
    VULNS=$(curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID/vulnerabilities" \
      -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities | length')

    CRITICAL=$(curl -s "$DTRACK_URL/api/v1/project/$PROJECT_UUID/vulnerabilities?severity=CRITICAL" \
      -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities | length')

    LAST_UPDATE=$(echo "$project" | jq -r '.lastBomImportDate // "Never"')

    echo "Production,$PROJECT_NAME,$PROJECT_VERSION,$COMPONENTS,$VULNS,$CRITICAL,$LAST_UPDATE" >> inventory.csv

    echo "Processed $PROJECT_NAME"
  done

echo "Inventory export complete: inventory.csv"
cat inventory.csv
```

## Use Case 7: Dependency License Analysis

**Scenario**: Analyze licenses across all dependencies

```bash
#!/bin/bash

DTRACK_URL="https://dtrack.company.com"
DTRACK_API_KEY="api-key-here"

PROJECT_UUID="your-project-uuid"

# Get all components and their licenses
echo "=== License Analysis Report ==="
echo "Component,Version,License,Risky"

curl -s "$DTRACK_URL/api/v1/component?project=$PROJECT_UUID&limit=500" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '.components[] | {name, version, license: (.license // "Unknown")}' | \
  jq -r '.name + "," + .version + "," + .license + "," + (if [.license] | map(select(test("GPL|AGPL|SSPL"))) | length > 0 then "YES" else "NO" end)' | \
  column -t -s','

# Count licenses
echo ""
echo "=== License Summary ==="
curl -s "$DTRACK_URL/api/v1/component?project=$PROJECT_UUID&limit=500" \
  -H "Authorization: Bearer $DTRACK_API_KEY" | \
  jq '[.components[] | .license // "Unknown"] | group_by(.) | map({license: .[0], count: length}) | sort_by(.count) | reverse' | \
  jq '.[] | "\(.license): \(.count)"' -r
```

Each of these examples demonstrates real-world integration patterns and workflows with Dependency-Track.
