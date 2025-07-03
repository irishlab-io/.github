terraform {
  required_version = "1.10.2"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.6.0"
    }
  }
  backend "local" {
    path = "../../terraform.tfstate"
  }
}

provider "github" {
  token = var.GITHUB_TOKEN
}
