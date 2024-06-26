# Provided in inputs.tfvars (static, not sensitive) ----------------------------------------------

variable "app_name" {
  type = string
  description = "A name for the bot to be used in resource naming"
}

variable "libraries_layer_deployment_path" {
  type = string
}

variable "commons_layer_deployment_path" {
  type = string
}

variable "image_layer_deployment_path" {
  type = string
}

variable "discord_interaction_lambda_data" {
  type = object({
    handler: string
    path_to_deployment_package: string
    memory: number,
    timeout_seconds: number
  })
}

variable "scheduled_lambda_data" {
  type = object({
    handler: string
    path_to_deployment_package: string
    memory: number,
    timeout_seconds: number
  })
}

variable "command_data" {
  type = list(object({
    command_name: string # Terraform friendly command name
    command_name_discord: string # command name as it is in Discord
    handler: string # path to handler
    memory: number # amount of memory in MB
    package_zip_name: string # deployment ZIP name
    timeout_seconds: number # lambda timeout
  }))
  description = "All the commands that the bot must process"
}

variable "discord_interaction_path" {
  type = string
  description = "URL path of the Discord interaction webhook. Must be relative and not start with '/'"
}

variable "parameter_update_interaction_path" {
  type = string
  description = "URL path for SSM parameter update. Must be relative and not start with '/'"
}

variable "log_retention_days" {
  type = number
  description = "How long to keep CloudWatch logs"
}

# Provided from command line arguments (dynamic or sensitive) ---------------------------------------

variable "aws_region" {
  type = string
  description = "Deployment AWS region"
}

variable "environment" {
  type = string
  description = "Deployment environment for example 'prd'"
}

variable "discord_bot_token" {
  type = string
  sensitive = true
  description = "The Bot token that authorizes the bot to communicate with the Discord API"
}

variable "aws_key_id" {
  type = string
  sensitive = true
  description = "AWS access key ID"
}

variable "aws_secret_key" {
  type = string
  sensitive = true
  description = "AWS secret key"
}

variable "aws_terraform_role_arn" {
  type = string
  description = "ARN of the role Terraform must assume"
}

variable "aws_assume_role_external_id" {
  type = string
  sensitive = true
  description = "Secret required to assume the Terraform role"
}

variable "discord_application_id" {
  type = number
  description = "Number that is the ID of the Discord bot"
}

variable "discord_application_public_key" {
  type = string
  description = "Public key for the bot"
}

variable "discord_application_name" {
  type = string
  description = "The Bots name as it appears in Discord"
}

variable "developer_email_address" {
  type = string
  description = "Email of developer that is subscribed to SNS topics such as error topic"
}

variable "parameter_store_name_prefix" {
  type = string
  description = "All the parameter store names will be prefixed with this string (and additionally the environment name)"
}

variable "bot_api_token" {
  type = string
  sensitive = true
  description = "API token for the bots own API, for example to update SSM parameters"
}