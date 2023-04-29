variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

# Free tier maximum is 25 read and 25 write units in TOTAL
# includes both environments of course

variable "dynamodb_read_capacity" {
  type = number
  default = 6
}

variable "dynamodb_write_capacity" {
  type = number
  default = 6
}

variable "gw2_users_hash_key" {
  type = string
  default = "UserId"
}

variable "gw2_guilds_hash_key" {
  type = string
  default = "GuildId"
}
