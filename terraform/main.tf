locals {
  libraries_layer_package_path = "${path.module}/${var.libraries_layer_deployment_path}"
  common_layer_package_path = "${path.module}/${var.commons_layer_deployment_path}"
  image_layer_package_path = "${path.module}/${var.image_layer_deployment_path}"

  discord_interaction_lambda_package_path = "${path.module}/${var.discord_interaction_lambda_data.path_to_deployment_package}"
  scheduled_lambda_package_path = "${path.module}/${var.scheduled_lambda_data.path_to_deployment_package}"
  command_lambda_path_prefix = "${path.module}/../command-lambda-packages"
}

module "s3" {
  source = "./s3"
  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment
  path_to_app_icon = "${path.module}/../static/commander.png"
  key_of_app_icon = "app_icon.png"
}

module "dynamodb_tables" {
  source = "./dynamodb"
  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment
}

module "sns" {
  source = "./sns"
  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment
  developer_email_address = var.developer_email_address
}

module "scheduled_lambda" {
  source = "./scheduled_lambda"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  handler_name = var.scheduled_lambda_data.handler
  memory = var.scheduled_lambda_data.memory
  path_to_deployment_package = local.scheduled_lambda_package_path
  dead_letter_error_topic_arn = module.sns.error_topic_arn

  libraries_layer_arn = aws_lambda_layer_version.libraries_lambda_layer.arn
  common_layer_arn = aws_lambda_layer_version.common_lambda_layer.arn

  environment_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
    GW2_USERS_TABLE_NAME = module.dynamodb_tables.gw2_users_table_name
    GW2_GUILDS_TABLE_NAME = module.dynamodb_tables.gw2_guilds_table_name
    APP_NAME = var.discord_application_name
    APP_ICON_URL = module.s3.app_icon_url
  }
  log_retention_days = var.log_retention_days
  gw2_users_table_arn = module.dynamodb_tables.gw2_users_table_arn
  gw2_guilds_table_arn = module.dynamodb_tables.gw2_guilds_table_arn
}

module "scheduler" {
  source = "./event_bridge_scheduler"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  scheduled_lambda_arn = module.scheduled_lambda.scheduled_lambda_arn
}

# The lambda layer that contains the required libraries
resource "aws_lambda_layer_version" "libraries_lambda_layer" {
  layer_name = "Libraries-${var.app_name}-${var.environment}-${var.aws_region}"
  filename = local.libraries_layer_package_path
  source_code_hash = filebase64sha256(local.libraries_layer_package_path)
  compatible_runtimes = ["python3.9"]
}

# The lambda layer that contains the 'commons' module
resource "aws_lambda_layer_version" "common_lambda_layer" {
  layer_name = "Commons-${var.app_name}-${var.environment}-${var.aws_region}"
  filename = local.common_layer_package_path
  source_code_hash = filebase64sha256(local.common_layer_package_path)
  compatible_runtimes = ["python3.9"]
}

# The lambda layer that contains the image processing libraries
resource "aws_lambda_layer_version" "image_lambda_layer" {
  layer_name = "Image-${var.app_name}-${var.environment}-${var.aws_region}"
  filename = local.image_layer_package_path
  source_code_hash = filebase64sha256(local.image_layer_package_path)
  compatible_runtimes = ["python3.9"]
}

# Build a lambda function for each command
module "command_lambda_modules" {
  count = length(var.command_data)
  source = "./command_handler_lambda"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  command_name = var.command_data[count.index].command_name
  command_name_discord = var.command_data[count.index].command_name_discord
  handler_name = var.command_data[count.index].handler
  memory = var.command_data[count.index].memory
  timeout_seconds = var.command_data[count.index].timeout_seconds
  path_to_deployment_package = "${local.command_lambda_path_prefix}/${var.command_data[count.index].package_zip_name}"
  dead_letter_error_topic_arn = module.sns.error_topic_arn

  # in the pre-defined map, find the policy and the variables for this lambda
  layer_arns = local.lambda_environments[var.command_data[count.index].command_name]["layers"]
  command_policy = local.lambda_environments[var.command_data[count.index].command_name]["policy"]
  environment_variables = local.lambda_environments[var.command_data[count.index].command_name]["variables"]
  log_retention_days = var.log_retention_days
}

# This object will be encoded into JSON and put into the Discord Interaction lambda
# contains the data about all commands and the lambda functions related to them
locals {
  command_lambda_functions_data = [
    for command_lambda_module in module.command_lambda_modules: {
      command_name_discord = command_lambda_module.command_name_discord
      command_lambda_arn = command_lambda_module.command_handler_lambda_arn
    }
  ]
}

# Build the lambda function that will distribute calls to command functions ("Discord Interaction" lambda)
module "discord_interaction_lambda" {
  source = "./discord_interaction_lambda"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  handler_name = var.discord_interaction_lambda_data.handler
  memory = var.discord_interaction_lambda_data.memory
  path_to_deployment_package = local.discord_interaction_lambda_package_path
  dead_letter_error_topic_arn = module.sns.error_topic_arn

  libraries_layer_arn = aws_lambda_layer_version.libraries_lambda_layer.arn
  common_layer_arn = aws_lambda_layer_version.common_lambda_layer.arn

  command_handler_lambda_arns = [for command_handler in module.command_lambda_modules: command_handler.command_handler_lambda_arn]
  environment_variables = {
    APPLICATION_ID = var.discord_application_id
    BOT_TOKEN = var.discord_bot_token
    APPLICATION_PUBLIC_KEY = var.discord_application_public_key
    COMMANDS = jsonencode(local.command_lambda_functions_data)
  }
  log_retention_days = var.log_retention_days
}

module "api_gateway" {
  source = "./api_gateway"

  app_name = var.app_name
  aws_region = var.aws_region
  environment = var.environment

  discord_interaction_lambda_name = module.discord_interaction_lambda.discord_interaction_lambda_name
  discord_interaction_lambda_invocation_arn = module.discord_interaction_lambda.discord_interaction_lambda_invoke_arn
  discord_interaction_path = var.discord_interaction_path
  log_retention_days = var.log_retention_days
}