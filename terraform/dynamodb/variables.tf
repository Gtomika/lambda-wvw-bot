variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "dynamodb_read_capacity" {
  type = number
  default = 5
}

variable "dynamodb_write_capacity" {
  type = number
  default = 5
}

variable "gw2_users_hash_key" {
  type = string
  default = "UserId"
}
