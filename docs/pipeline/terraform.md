# Terraform Workflows

Two reusable GitHub Actions workflows handle the Terraform lifecycle in CI/CD:

| Workflow | File | Purpose |
|---|---|---|
| **Terraform Plan** | `reusable-terraform-plan.yml` | `fmt`, `init`, `validate`, `plan` — posts result to the PR |
| **Terraform Apply** | `reusable-terraform-apply.yml` | `init`, `apply` — protected by a GitHub Environment |

## Storing Terraform State (tfstate)

The recommended backend is **AWS S3 + DynamoDB**.

| Component | Purpose |
|---|---|
| **S3 bucket** | Remote state storage |
| **DynamoDB table** | State locking (prevents concurrent runs) |
| **IAM role (OIDC)** | Keyless authentication from GitHub Actions |

### Minimal AWS backend configuration

```hcl
# backend.tf
terraform {
  backend "s3" {
    # Values are supplied at runtime via -backend-config flags
    # to keep this file environment-agnostic
  }
}
```

Create the S3 bucket and DynamoDB table once per AWS account (example with the AWS CLI):

```bash
# State bucket — enable versioning and encryption
aws s3api create-bucket \
  --bucket my-org-tfstate \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

aws s3api put-bucket-versioning \
  --bucket my-org-tfstate \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket my-org-tfstate \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}'

# Lock table
aws dynamodb create-table \
  --table-name my-org-tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-west-1
```

### OIDC IAM role

Allow GitHub Actions to assume an IAM role without storing long-lived AWS credentials as secrets.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:*"
        }
      }
    }
  ]
}
```

> [!TIP]
> Tighten the `sub` condition to restrict access to specific branches or environments, e.g.
> `repo:my-org/my-repo:environment:production` for apply-only roles.

The role needs at minimum the following permissions on the state resources:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-org-tfstate",
        "arn:aws:s3:::my-org-tfstate/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"],
      "Resource": "arn:aws:dynamodb:eu-west-1:<ACCOUNT_ID>:table/my-org-tfstate-lock"
    }
  ]
}
```

## Required Repository Secrets

| Secret | Description |
|---|---|
| `AWS_ROLE_ARN` | Full ARN of the IAM role to assume via OIDC |

## Usage

### Plan on pull requests

```yaml
# .github/workflows/pr.yml
jobs:
  terraform-plan:
    name: Terraform Plan
    uses: irishlab-io/.github/.github/workflows/reusable-terraform-plan.yml@main
    with:
      working-directory: infra/envs/staging
      aws-region: eu-west-1
      environment: staging
      terraform-version: "1.11.0"
      backend-config: |
        bucket=my-org-tfstate
        key=envs/staging/terraform.tfstate
        region=eu-west-1
        dynamodb_table=my-org-tfstate-lock
      terraform-var-file: staging.tfvars
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_STAGING }}
```

### Apply on merge to main

```yaml
# .github/workflows/main.yml
jobs:
  terraform-apply:
    name: Terraform Apply
    uses: irishlab-io/.github/.github/workflows/reusable-terraform-apply.yml@main
    with:
      working-directory: infra/envs/staging
      aws-region: eu-west-1
      environment: staging        # enforces required reviewers if configured
      terraform-version: "1.11.0"
      backend-config: |
        bucket=my-org-tfstate
        key=envs/staging/terraform.tfstate
        region=eu-west-1
        dynamodb_table=my-org-tfstate-lock
      terraform-var-file: staging.tfvars
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_STAGING }}
```

### Full plan → apply pipeline with environment protection

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  plan:
    name: Terraform Plan
    uses: irishlab-io/.github/.github/workflows/reusable-terraform-plan.yml@main
    with:
      working-directory: infra/envs/production
      environment: production
      backend-config: |
        bucket=my-org-tfstate
        key=envs/production/terraform.tfstate
        region=eu-west-1
        dynamodb_table=my-org-tfstate-lock
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_PROD }}

  apply:
    needs: plan
    name: Terraform Apply
    uses: irishlab-io/.github/.github/workflows/reusable-terraform-apply.yml@main
    with:
      working-directory: infra/envs/production
      environment: production   # blocks until required reviewers approve
      backend-config: |
        bucket=my-org-tfstate
        key=envs/production/terraform.tfstate
        region=eu-west-1
        dynamodb_table=my-org-tfstate-lock
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_PROD }}
```

## Inputs Reference

### `reusable-terraform-plan.yml`

| Input | Required | Default | Description |
|---|---|---|---|
| `working-directory` | No | `.` | Directory containing terraform files |
| `terraform-version` | No | `latest` | Terraform version to install |
| `aws-region` | No | `eu-west-1` | AWS region for OIDC and backend |
| `environment` | No | `""` | GitHub environment (enables protection rules) |
| `backend-config` | No | `""` | Multi-line `key=value` backend config |
| `terraform-var-file` | No | `""` | Path to a `.tfvars` file |

### `reusable-terraform-apply.yml`

Same inputs as plan — `pull-requests: write` permission is not required.

## PR Comment

The plan workflow automatically creates (or updates) a PR comment showing the step outcomes and the full plan output:

```text
🏗️ Terraform Plan — `infra/envs/staging` (`staging`)

| Step     | Status       |
|----------|--------------|
| 📐 Format  | ✅ success   |
| ⚙️ Init    | ✅ success   |
| 🔍 Validate | ✅ success   |
| 📋 Plan    | ✅ success   |

<details><summary>Show Plan Output</summary>
...
</details>
```

> [!NOTE]
> The comment is updated on each push to the PR — only one comment per `working-directory` is kept.
