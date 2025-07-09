variable "repository_name" {
  description = "The name of the GitHub repository."
  type        = string
}

variable "required_status_checks" {
  description = "A list of required status checks."
  type        = list(string)
}

variable "required_code_scanning_tools" {
  description = "A list of required code scanning tools."
  type        = list(string)
}
