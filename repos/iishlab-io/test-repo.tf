resource "github_repository" "test-repo" {
  name        = "test-repo"
  description = "A test-repo"
  visibility  = "public"
  homepage_url = "https://exemple.com"

  # Repository Features
  has_issues   = true
  has_projects = false

  # Pull Request settings
  allow_auto_merge            = true
  allow_merge_commit          = false
  allow_rebase_merge          = false
  allow_update_branch         = true
  delete_branch_on_merge      = true
  squash_merge_commit_message = "PR_BODY"
  squash_merge_commit_title   = "PR_TITLE"

  # Security settings
  security_and_analysis {
    secret_scanning {
      status = "enabled"
    }
    secret_scanning_push_protection {
      status = "enabled"
    }
  }

  # Other settings
  has_downloads               = false
  vulnerability_alerts        = true
  web_commit_signoff_required = true
}

module "test-repo_default_branch_protection" {
  source = "../modules/rulesets"

  repository_name = github_repository.test-repo.name
  required_status_checks = [
    "Check Code Quality",
    "CodeQL Analysis (actions) / Analyse code",
    "Common Code Checks / Check GitHub Actions with Actionlint",
    "Common Code Checks / Check GitHub Actions with zizmor",
    "Common Code Checks / Check Justfile Format",
    "Common Code Checks / Check Markdown links",
    "Common Code Checks / Lefthook Validate",
    "Common Code Checks / Pinact Check",
    "Common Pull Request Tasks / Dependency Review",
    "Common Pull Request Tasks / Label Pull Request",
  ]
  required_code_scanning_tools = ["CodeQL", "zizmor"]

  depends_on = [github_repository.test-repo]
}

resource "github_repository_dependabot_security_updates" "test-repo" {
  repository = github_repository.test-repo.name
  enabled    = true
}
