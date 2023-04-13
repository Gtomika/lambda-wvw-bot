variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "scheduled_lambda_arn" {
  type = string
  description = "ARN of the scheduler lambda, that executes all scheduled tasks"
}

variable "scheduler_lambda_target" {
  type = string
  default = "arn:aws:scheduler:::aws-sdk:lambda:invoke"
}

variable "time_zone" {
  type = string
  default = "Europe/Budapest" # TODO: how to localize it?
}

variable "wvw_reset_cron" {
  type = string
  default = "30 18 * * FRI *"
  description = "Every friday at 18:30, this way it works no matter if reset is 19:00 or 20:00"
}