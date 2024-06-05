variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "log_retention_days" {
  type = number
  description = "How long to keep CloudWatch logs"
}

variable "discord_interaction_lambda_name" {
  type = string
}

variable "discord_interaction_lambda_invocation_arn" {
  type = string
  default = "Invocation ARN of the Discord interaction lambda: the API gateway must call it"
}

variable "discord_interaction_path" {
  type = string
  description = "URL path of the Discord interaction webhook. Must be relative and not start with '/'"
}

variable "scheduled_lambda_name" {
  type = string
}

variable "scheduled_lambda_invocation_arn" {
  type = string
  default = "Invocation ARN of the scheduled lambda: the API gateway must call it"
}

variable "parameter_update_interaction_path" {
  type = string
  description = "URL path for SSM parameter updated. Must be relative and not start with '/'"
}