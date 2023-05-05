variable "aws_region" {
  type = string
}

variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "path_to_app_icon" {
  type = string
}

variable "key_of_app_icon" {
  type = string
  description = "app_icon.png"
}

variable "map_images_prefix" {
  type = string
  default = "map_images/"
}

variable "map_images_expiration_days" {
  type = number
  default = 10
}