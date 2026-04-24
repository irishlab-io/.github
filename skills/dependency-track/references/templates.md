# Dependency-Track Setup Templates

## Quick Start Script

Use this script to automate the complete Dependency-Track setup for new projects:

```bash
#!/bin/bash

# Configuration
DTRACK_URL="https://dtrack.example.com"
DTRACK_API_KEY="your-api-key-here"
PARENT_NAME="Your Organization"
PROJECT_NAME="Your Project"
PROJECT_VERSION="1.0.0"
GITHUB_REPO="https://github.com/owner/repo"
SBOM_FILE="./sbom.json"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to detect API authentication format
detect_api_format() {
  # Try modern X-API-Key format first
  if curl -s "$DTRACK_URL/api/v1/project?limit=1" \
    -H "X-API-Key: $DTRACK_API_KEY" > /dev/null 2>&1; then
    echo "x-api-key"
  else
    echo "bearer"
  fi
}

API_FORMAT=$(detect_api_format)
echo -e "${BLUE}Detected API format: $API_FORMAT${NC}"

# Function to make API calls
dtrack_api() {
  local method=$1
  local endpoint=$2
  local data=$3

  # Determine authentication header
  if [ "$API_FORMAT" = "x-api-key" ]; then
    local auth_header="X-API-Key: $DTRACK_API_KEY"
  else
    local auth_header="Authorization: Bearer $DTRACK_API_KEY"
  fi

  if [ -z "$data" ]; then
    curl -s -X "$method" "$DTRACK_URL/api/v1$endpoint" \
      -H "$auth_header" \
      -H "Content-Type: application/json"
  else
    curl -s -X "$method" "$DTRACK_URL/api/v1$endpoint" \
      -H "$auth_header" \
      -H "Content-Type: application/json" \
      -d "$data"
  fi
}

# Function to upload SBOM with error handling
upload_sbom() {
  local project_uuid=$1
  local sbom_path=$2

  echo -e "${BLUE}Uploading SBOM...${NC}"
  echo -e "${YELLOW}Note: If this returns 404, see Known Issues in documentation${NC}"

  # Determine authentication header for multipart upload
  if [ "$API_FORMAT" = "x-api-key" ]; then
    local auth_header="X-API-Key: $DTRACK_API_KEY"
  else
    local auth_header="Authorization: Bearer $DTRACK_API_KEY"
  fi

  local response=$(curl -s -w "\n%{http_code}" -X POST "$DTRACK_URL/api/v1/bom" \
    -H "$auth_header" \
    -F "projectUuid=$project_uuid" \
    -F "bom=@$sbom_path" \
    -F "bomFormat=CycloneDX" \
    -F "bomSpecVersion=1.4")

  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | head -n-1)

  echo "$body" | jq '.'

  if [ "$http_code" = "404" ]; then
    echo -e "${YELLOW}⚠️  SBOM upload returned 404. This may be v4.14.1 server bug.${NC}"
    echo -e "${YELLOW}Workaround: Use web UI (Login → Projects → Upload SBOM)${NC}"
    return 1
  elif [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    echo -e "${YELLOW}⚠️  SBOM upload returned HTTP $http_code${NC}"
    return 1
  fi
  return 0
}

# Step 1: Create Parent Project
echo -e "${BLUE}Step 1: Creating parent project...${NC}"
PARENT_RESPONSE=$(dtrack_api POST "/project" "{
  \"name\": \"$PARENT_NAME\",
  \"description\": \"Parent project for organizing related projects\",
  \"version\": \"1.0.0\",
  \"tags\": [\"parent\", \"organization\"]
}")

PARENT_UUID=$(echo "$PARENT_RESPONSE" | jq -r '.uuid')
echo -e "${GREEN}Parent Project UUID: $PARENT_UUID${NC}"

# Step 2: Create Child Project
echo -e "${BLUE}Step 2: Creating child project...${NC}"
PROJECT_RESPONSE=$(dtrack_api POST "/project" "{
  \"name\": \"$PROJECT_NAME\",
  \"description\": \"Description of your project\",
  \"version\": \"$PROJECT_VERSION\",
  \"parent\": {\"uuid\": \"$PARENT_UUID\"},
  \"tags\": [\"production\", \"critical\"]
}")

PROJECT_UUID=$(echo "$PROJECT_RESPONSE" | jq -r '.uuid')
echo -e "${GREEN}Child Project UUID: $PROJECT_UUID${NC}"

# Step 3: Upload SBOM
if [ -f "$SBOM_FILE" ]; then
  upload_sbom "$PROJECT_UUID" "$SBOM_FILE"
else
  echo -e "${BLUE}SBOM file not found at $SBOM_FILE, skipping...${NC}"
fi

# Step 4: Add External References
echo -e "${BLUE}Step 4: Adding external references...${NC}"

# VCS Reference
echo "Adding VCS reference..."
dtrack_api POST "/project/$PROJECT_UUID/externalReferences" "{
  \"type\": \"VCS\",
  \"url\": \"$GITHUB_REPO\"
}" | jq '.type'

# Issue Tracker Reference
echo "Adding Issue Tracker reference..."
dtrack_api POST "/project/$PROJECT_UUID/externalReferences" "{
  \"type\": \"ISSUE_TRACKER\",
  \"url\": \"$GITHUB_REPO/issues\"
}" | jq '.type'

# Documentation Reference
echo "Adding Documentation reference..."
dtrack_api POST "/project/$PROJECT_UUID/externalReferences" "{
  \"type\": \"DOCUMENTATION\",
  \"url\": \"https://docs.example.com\"
}" | jq '.type'

echo -e "${GREEN}Setup complete!${NC}"
echo -e "Parent Project: $PARENT_UUID"
echo -e "Child Project: $PROJECT_UUID"
echo -e "Dashboard: $DTRACK_URL/projects/$PROJECT_UUID"
```

## Environment Configuration Template

Create a `.env` file for your Dependency-Track setup:

```bash
# Dependency-Track Server
DTRACK_URL=https://dtrack.your-domain.com
DTRACK_API_KEY=your-api-key-here

# Parent Project Configuration
PARENT_PROJECT_NAME=Your Organization Name
PARENT_PROJECT_VERSION=1.0.0
PARENT_PROJECT_TAGS=parent,organization

# Project Defaults
DEFAULT_PROJECT_VERSION=1.0.0
DEFAULT_PROJECT_TAGS=production,critical
DEFAULT_MANUFACTURER=Your Organization

# GitHub Configuration
GITHUB_ORG=your-org
GITHUB_BASE_URL=https://github.com

# SBOM Generation
SBOM_FORMAT=cyclonedx
SBOM_VERSION=1.4
SBOM_OUTPUT_DIR=./sboms
```

Load the configuration:
```bash
source .env
```

## Bash Helper Functions

Save these functions in a `dtrack-helpers.sh` file for reuse:

```bash
#!/bin/bash

# Source configuration
if [ -f ".env" ]; then
  source .env
fi

# Validate configuration
validate_config() {
  if [ -z "$DTRACK_URL" ] || [ -z "$DTRACK_API_KEY" ]; then
    echo "Error: DTRACK_URL and DTRACK_API_KEY not set"
    exit 1
  fi
  echo "Configuration valid ✓"
}

# Create parent project
create_parent_project() {
  local name=$1
  local description=${2:-"Parent project for organizing related projects"}
  local version=${3:-"1.0.0"}

  echo "Creating parent project: $name"
  local response=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"description\": \"$description\", \"version\": \"$version\"}")

  echo "$response" | jq -r '.uuid'
}

# Create child project
create_child_project() {
  local name=$1
  local parent_uuid=$2
  local description=${3:-""}
  local version=${4:-"1.0.0"}

  echo "Creating child project: $name"
  local response=$(curl -s -X POST "$DTRACK_URL/api/v1/project" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"parent\": {\"uuid\": \"$parent_uuid\"}, \"description\": \"$description\", \"version\": \"$version\"}")

  echo "$response" | jq -r '.uuid'
}

# Upload SBOM
upload_sbom() {
  local project_uuid=$1
  local sbom_file=$2

  if [ ! -f "$sbom_file" ]; then
    echo "Error: SBOM file not found: $sbom_file"
    return 1
  fi

  echo "Uploading SBOM: $sbom_file"
  curl -s -X POST "$DTRACK_URL/api/v1/bom" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -F "projectUuid=$project_uuid" \
    -F "bom=@$sbom_file" \
    -F "bomFormat=CycloneDX" \
    -F "bomSpecVersion=1.4" | jq '.'
}

# Add external reference
add_external_reference() {
  local project_uuid=$1
  local ref_type=$2
  local url=$3

  echo "Adding external reference: $ref_type -> $url"
  curl -s -X POST "$DTRACK_URL/api/v1/project/$project_uuid/externalReferences" \
    -H "Authorization: Bearer $DTRACK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"$ref_type\", \"url\": \"$url\"}" | jq '.type'
}

# Get project details
get_project() {
  local project_uuid=$1

  curl -s -X GET "$DTRACK_URL/api/v1/project/$project_uuid" \
    -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.'
}

# List components
list_components() {
  local project_uuid=$1

  curl -s -X GET "$DTRACK_URL/api/v1/component?project=$project_uuid" \
    -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.components[] | {name, version, license}'
}

# Get vulnerabilities
get_vulnerabilities() {
  local project_uuid=$1
  local severity=${2:-""}

  local url="$DTRACK_URL/api/v1/project/$project_uuid/vulnerabilities"
  if [ -n "$severity" ]; then
    url="$url?severity=$severity"
  fi

  curl -s -X GET "$url" \
    -H "Authorization: Bearer $DTRACK_API_KEY" | jq '.vulnerabilities[] | {title, severity, cve, status}'
}

# Export configuration (for CI/CD pipelines)
export_config() {
  echo "DTRACK_URL=$DTRACK_URL"
  echo "DTRACK_API_KEY=****" # Don't export the key
}
```

Usage in scripts:
```bash
source dtrack-helpers.sh
validate_config
PARENT_ID=$(create_parent_project "My Organization")
PROJECT_ID=$(create_child_project "My Project" "$PARENT_ID")
upload_sbom "$PROJECT_ID" "./sbom.json"
add_external_reference "$PROJECT_ID" "VCS" "https://github.com/owner/repo"
```

## Project Creation Template

JSON template for creating projects programmatically:

```json
{
  "parent_project": {
    "name": "Organization Name",
    "description": "Parent project for all related projects",
    "version": "1.0.0",
    "tags": ["parent", "organization"]
  },
  "child_projects": [
    {
      "name": "Backend API",
      "description": "RESTful API service",
      "version": "2.1.0",
      "tags": ["production", "critical", "java", "api"],
      "manufacturer": "Engineering Team",
      "classifier": "application",
      "external_references": [
        {
          "type": "VCS",
          "url": "https://github.com/owner/backend-api"
        },
        {
          "type": "ISSUE_TRACKER",
          "url": "https://github.com/owner/backend-api/issues"
        },
        {
          "type": "DOCUMENTATION",
          "url": "https://api.example.com/docs"
        },
        {
          "type": "BUILD_SYSTEM",
          "url": "https://github.com/owner/backend-api/actions"
        }
      ]
    },
    {
      "name": "Mobile App",
      "description": "iOS and Android native apps",
      "version": "1.5.0",
      "tags": ["production", "critical", "mobile"],
      "manufacturer": "Mobile Team",
      "classifier": "application"
    }
  ]
}
```

## GitHub Actions Integration

Example workflow to upload SBOM to Dependency-Track on release:

```yaml
name: Upload SBOM to Dependency-Track

on:
  release:
    types: [published]

jobs:
  upload-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

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
```

## SBOM Validation Script

Validate SBOM files before uploading:

```bash
#!/bin/bash

SBOM_FILE=$1

if [ ! -f "$SBOM_FILE" ]; then
  echo "Error: SBOM file not found: $SBOM_FILE"
  exit 1
fi

# Check if JSON is valid (preferred format)
if [[ "$SBOM_FILE" == *.json ]]; then
  if ! jq empty "$SBOM_FILE" 2>/dev/null; then
    echo "Error: Invalid JSON in SBOM file"
    exit 1
  fi
  echo "✓ JSON is valid"
fi

# Check if XML is valid
if [[ "$SBOM_FILE" == *.xml ]]; then
  if ! xmllint --noout "$SBOM_FILE" 2>/dev/null; then
    echo "Error: Invalid XML in SBOM file"
    exit 1
  fi
  echo "✓ XML is valid"
fi

# Check for required CycloneDX elements
if grep -q "cyclonedx" "$SBOM_FILE"; then
  echo "✓ CycloneDX format detected"

  # Check for components section
  if grep -q "<components>" "$SBOM_FILE" || grep -q '"components"' "$SBOM_FILE"; then
    COMPONENT_COUNT=$(grep -o "<component>" "$SBOM_FILE" | wc -l)
    [ "$COMPONENT_COUNT" -eq 0 ] && COMPONENT_COUNT=$(jq '.metadata.component // .components | length' "$SBOM_FILE")
    echo "✓ Found $COMPONENT_COUNT components"
  else
    echo "⚠ No components section found in SBOM"
  fi
fi

# Check for SPDX format
if grep -q "spdxVersion" "$SBOM_FILE"; then
  echo "✓ SPDX format detected"
fi

echo "✓ SBOM validation complete"
```

Usage:
```bash
./validate-sbom.sh sbom.json
```
