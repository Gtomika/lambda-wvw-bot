variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "layer_arns" {
  type = list(string)
}

variable "command_name" {
  type = string
  description = "A name for this slash command, to be used in resource namings."
}

variable "command_name_discord" {
  type = string
  default = "A name for this slash command, as used in Discord"
}

variable "command_policy" {
  description = "Should be a 'data.aws_iam_policy_document' where 'sid' is always provided. Must not contain the logging policy, the module adds that."
}

variable "path_to_deployment_package" {
  type = string
}

variable "handler_name" {
  type = string
}

variable "memory" {
  type = number
}

variable "environment_variables" {
  type = map(string)
}

variable "log_retention_days" {
  type = number
  description = "How long to keep CloudWatch logs"
}

variable "timeout_seconds" {
  type = number
}