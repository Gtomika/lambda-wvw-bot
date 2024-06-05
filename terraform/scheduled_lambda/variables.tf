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

variable "common_layer_arn" {
  type = string
}

variable "libraries_layer_arn" {
  type = string
}

variable "log_retention_days" {
  type = number
}

variable "gw2_users_table_arn" {
  type = string
}

variable "gw2_guilds_table_arn" {
  type = string
}

variable "dead_letter_error_topic_arn" {
  type = string
}

variable "bot_ssm_parameters_prefix" {
  type = string
}
