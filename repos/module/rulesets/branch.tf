resource "github_repository_ruleset" "default_ruleset" {
  name        = "Protect default branch"
  repository  = var.repository_name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  bypass_actors {
    actor_id    = 5
    actor_type  = "RepositoryRole"
    bypass_mode = "pull_request"
  }

  rules {
    creation                = false
    update                  = false
    deletion                = true
    non_fast_forward        = true
    required_linear_history = true
    required_signatures     = true

    pull_request {
      dismiss_stale_reviews_on_push     = true
      require_code_owner_review         = false
      require_last_push_approval        = false
      required_approving_review_count   = 0
      required_review_thread_resolution = true
    }

    required_status_checks {
      strict_required_status_checks_policy = true

      dynamic "required_check" {
        for_each = var.required_status_checks
        content {
          context        = required_check.value
          integration_id = 15368
        }
      }
    }

    required_code_scanning {
      dynamic "required_code_scanning_tool" {
        for_each = var.required_code_scanning_tools
        content {
          tool                      = required_code_scanning_tool.value
          alerts_threshold          = "all"
          security_alerts_threshold = "all"
        }
      }
    }
  }
}
