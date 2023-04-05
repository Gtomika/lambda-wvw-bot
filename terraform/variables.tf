# Provided in inputs.tfvars (static, not sensitive) ----------------------------------------------

variable "app_name" {
  type = string
  description = "A name for the bot to be used in resource naming"
}

variable "commons_layer_deployment_path" {
  type = string
}

variable "discord_interaction_lambda_data" {
  type = object({
    handler: string
    path_to_deployment_package: string
  })
}

variable "command_data" {
  type = list(object({
    command_name: string # Terraform friendly command name
    command_name_discord: string # command name as it is in Discord
    handler: string # path to handler
    path_to_deployment_package: string # deployment ZIP path relative to terraform root module
  }))
  description = "All the commands that the bot must process"
}

variable "discord_interaction_path" {
  type = string
  description = "URL path of the Discord interaction webhook. Must be relative and not start with '/'"
}

variable "discord_developer_id" {
  type = number
  description = "Discord ID of developer who is mentioned by the bot"
}

variable "documentation_url" {
  type = string
  description = "Link to bots documentation"
}

variable "gw2_required_permissions" {
  type = string
  description = "All permissions that the GW2 API key must have to use all bot functionality"
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

variable "log_retention_days" {
  type = number
  description = "How long to keep CloudWatch logs"
}

variable "discord_application_id" {
  type = number
  description = "Number that is the ID of the Discord bot"
}

variable "discord_application_public_key" {
  type = string
  description = "Public key for the bot"
}