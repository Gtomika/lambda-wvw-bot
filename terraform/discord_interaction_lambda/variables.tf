variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
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

variable "timeout_seconds" {
  type = number
}

variable "environment_variables" {
  type = map(string)
}

variable "command_handler_lambda_arns" {
  type = list(string)
}

variable "common_layer_arn" {
  type = string
}

variable "libraries_layer_arn" {
  type = string
}

variable "log_retention_days" {
  type = number
  description = "How long to keep CloudWatch logs"
}

variable "dead_letter_error_topic_arn" {
  type = string
}