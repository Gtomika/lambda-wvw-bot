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

variable "environment_variables" {
  type = map(string)
}

variable "common_layer_arn" {
  type = string
}

variable "log_retention_days" {
  type = number
}
